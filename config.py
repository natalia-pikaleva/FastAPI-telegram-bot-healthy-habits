import os
from dotenv import load_dotenv, find_dotenv
import logging
import logging.config
import redis

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
DB_USER = os.getenv("DB_USER", )
DB_PASSWORD = os.getenv("DB_PASSWORD", )
DB_NAME = os.getenv("DB_NAME", )
API_HOST = os.getenv("API_HOST", "127.0.0.1")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")

BOT_TOKEN = os.getenv("BOT_TOKEN")


redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

DEFAULT_COMMANDS = (("start", "Меню"),
                    ("create_habit", "✍️ Создать новую привычку"),
                    ("habits_list", "📋 Все привычки"),
                    ("unmarked_habits", "⚪️ Привычки без отметки"),
                    ("statistics", "📈 Статистика"),
                    ("help", "😊 Обо мне"))

EXIT_COMMANDS = ["Меню", "✍️ Создать новую привычку", "📋 Все привычки",
                 "⚪️ Привычки без отметки", "📈 Статистика", "😊 Обо мне",
                 "/start", "/create_habit", "/habits_list", "/unmarked_habits",
                 "/statistics", "/help"]

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
