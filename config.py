import os
from dotenv import load_dotenv, find_dotenv
import logging
import logging.config

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
DB_USER = os.getenv("DB_USER", )
DB_PASSWORD = os.getenv("DB_PASSWORD", )
DB_NAME = os.getenv("DB_NAME", )
API_HOST = os.getenv("API_HOST", "127.0.0.1")
DB_HOST = "localhost"

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

DEFAULT_COMMANDS = (("start", "Меню"),
                    ("create_habit", "Создать новую привычку"),
                    ("habits_list", "Список всех привычек"),
                    ("unmarked_habits", "Список привычек без отметки"),
                    ("help", "Помощь"))

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s ----------[%(name)s] ---------- %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
