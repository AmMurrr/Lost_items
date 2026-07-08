import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.api import ApiClientError, ApiNotFoundError, get_item, search_items
from logs.logs import logger

load_dotenv()

SHOW_SIMILARITY = os.getenv("SHOW_SIMILARITY", "false").strip().lower() in {
    "1",
    "true",
}

LOSS_DATE, STATION, DESCRIPTION = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Пользователь открыл бота командой /start")
    await update.message.reply_text(
        """
        Здравствуйте!

        Я помогу проверить,
        не была ли найдена потерянная вещь.

        Для подачи заявки выполните /search. Для отмены поиска выполните /cancel.
        Что необходимо:

        1. Укажите дату потери.
        2. Укажите станцию метро, где была потеряна вещь.
        3. Опишите потерянную вещь.

        После этого я выполню поиск.
        """
    )


async def search_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data.clear()

    logger.info("Пользователь начал новый поиск командой /search")

    await update.message.reply_text("Введите дату потери в формате YYYY-MM-DD.")
    return LOSS_DATE


async def receive_loss_date(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    text = update.message.text.strip()

    try:
        loss_date = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text(
            "Неверный формат даты. Введите дату в формате YYYY-MM-DD."
        )
        return LOSS_DATE

    if loss_date.isoformat() != text:
        await update.message.reply_text(
            "Неверный формат даты. Введите дату в формате YYYY-MM-DD."
        )
        return LOSS_DATE

    context.user_data["loss_date"] = loss_date

    logger.info("Пользователь указал дату потери: %s", loss_date.isoformat())

    await update.message.reply_text("Введите станцию метро.")
    return STATION


async def receive_station(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    text = update.message.text.strip()
    words = text.split()

    if not words or not all(word.isalpha() for word in words):
        await update.message.reply_text(
            "Станция должна содержать только буквы и пробелы. Введите станцию еще раз."
        )
        return STATION

    station = " ".join(word.capitalize() for word in words)
    context.user_data["station"] = station

    logger.info("Пользователь указал станцию: %s", station)

    await update.message.reply_text("Опишите потерянную вещь.")
    return DESCRIPTION


async def receive_description(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    description = update.message.text.strip()

    if not description:
        await update.message.reply_text("Описание не должно быть пустым. Опишите вещь.")
        return DESCRIPTION

    context.user_data["description"] = description

    logger.info("Пользователь описал вещь, запускаю поиск")

    try:
        results = await search_items(
            description=context.user_data["description"],
            station=context.user_data["station"],
            loss_date=context.user_data["loss_date"],
        )
    except ApiClientError:
        logger.warning("Поиск завершился ошибкой на стороне API")
        await update.message.reply_text(
            "Сервис поиска временно недоступен. Попробуйте позже."
        )
        return ConversationHandler.END

    if not results:
        logger.info("Поиск не дал результатов")
        await update.message.reply_text("Похожих найденных вещей не обнаружено.")
        return ConversationHandler.END

    logger.info("Пользователю отправлены результаты поиска: %d", len(results))

    await update.message.reply_text(
        _format_search_results(results, show_similarity=SHOW_SIMILARITY),
        reply_markup=_build_results_keyboard(results),
    )

    return ConversationHandler.END


async def show_item_details(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    await query.answer()

    item_id = _parse_item_callback_data(query.data)

    if item_id is None:
        logger.warning("Не удалось разобрать callback с карточкой предмета")
        await query.message.reply_text("Не удалось определить выбранный предмет.")
        return

    logger.info("Пользователь запросил карточку предмета: id=%s", item_id)

    try:
        item = await get_item(item_id)
    except ApiNotFoundError:
        await query.message.reply_text("Предмет не найден.")
        return
    except ApiClientError:
        logger.warning("Не удалось получить карточку предмета из API: id=%s", item_id)
        await query.message.reply_text(
            "Сервис карточек временно недоступен. Попробуйте позже."
        )
        return

    text = _format_item_details(item)
    image_path = item.get("image_path")

    if image_path is None:
        await query.message.reply_text(text)
        return

    await _send_item_photo(
        update=update,
        image_path=image_path,
        caption=text,
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    logger.info("Пользователь отменил поиск")
    await update.message.reply_text("Поиск отменен.")
    return ConversationHandler.END


def get_search_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("search", search_start)],
        states={
            LOSS_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_loss_date)
            ],
            STATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_station)],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


def get_item_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(show_item_details, pattern=r"^item:\d+$")


def _format_search_results(results: list[dict], show_similarity: bool = False) -> str:
    lines = ["Найдены похожие вещи:\n"]

    for index, item in enumerate(results, start=1):
        lines.append(f"{index}. {_short_description(item['description'])}")

        if show_similarity and item.get("similarity") is not None:
            lines.append(f"Similarity: {float(item['similarity']):.3f}")

        lines.append("")

    return "\n".join(lines)


# Короткая версия описания для списка, только первую вещь
def _short_description(description: str) -> str:
    return description.split(",", 1)[0].strip()


def _build_results_keyboard(results: list[dict]) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(str(index), callback_data=f"item:{item['id']}")
            for index, item in enumerate(results, start=1)
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def _parse_item_callback_data(callback_data: str | None) -> int | None:
    if callback_data is None:
        return None

    prefix, separator, value = callback_data.partition(":")

    if prefix != "item" or separator != ":" or not value.isdigit():
        return None

    return int(value)


def _format_item_details(item: dict) -> str:
    return "\n".join(
        [
            f"Описание: {item.get('description', '-')}",
            f"Станция: {item.get('station', '-')}",
            f"Дата находки: {item.get('found_date', '-')}",
            f"Место обнаружения: {item.get('found_place', '-')}",
        ]
    )


async def _send_item_photo(
    update: Update,
    image_path: str,
    caption: str,
) -> None:
    query = update.callback_query
    path = Path(image_path)

    if path.is_file():
        with path.open("rb") as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=caption,
            )
        return

    await query.message.reply_photo(
        photo=image_path,
        caption=caption,
    )
