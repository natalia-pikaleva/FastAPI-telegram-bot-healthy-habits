import logging
from fastapi import Depends
from telebot.types import Message
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_user_by_chat_id
import requests
from config import setup_logging, API_HOST
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["help"])
def bot_help(message: Message) -> None:
    """
    Функция получает на входе команду help и возвращает пользователю справку
    """
    bot.send_message(chat_id=message.chat.id, text="Справка о работе бота")
