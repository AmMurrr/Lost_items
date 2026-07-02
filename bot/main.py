import os

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from bot.handlers import (
    get_item_callback_handler,
    get_search_conversation_handler,
    start,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise RuntimeError("Переменная окружения BOT_TOKEN не найдена")


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_search_conversation_handler())
    application.add_handler(get_item_callback_handler())

    application.run_polling()


if __name__ == "__main__":
    main()
