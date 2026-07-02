import os

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from bot.handlers import (
    get_item_callback_handler,
    get_search_conversation_handler,
    start,
)
from logs.logs import logger

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise RuntimeError("Переменная окружения BOT_TOKEN не найдена")


def main() -> None:
    logger.info("Инициализирую Telegram-бота")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_search_conversation_handler())
    application.add_handler(get_item_callback_handler())

    logger.info("Бот запущен и ожидает сообщения")

    try:
        application.run_polling()
    finally:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    main()
