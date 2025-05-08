import bot.handlers
import threading
from bot.setup import bot
from bot.utils import set_default_commands
from database.db_init import start_bd
from auth.router import router as auth_router
from fastapi import FastAPI
from config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])


def start_bot():
    logger.info("Starting Telegram bot polling")
    set_default_commands(bot)
    bot.infinity_polling(none_stop=True)


@app.on_event("startup")
def startup_event():
    """
    Запускаем бота и базу данных
    """
    try:
        logger.debug("Start startup_event function")
        # Запускаем инициализацию базы и ждём её окончания
        db_thread = threading.Thread(target=start_bd)
        db_thread.start()
        db_thread.join()

        # Запускаем бота в отдельном демоне
        threading.Thread(target=start_bot, daemon=True).start()
    except Exception as e:
        logger.error(f"Error during function startup_event: {e}")
