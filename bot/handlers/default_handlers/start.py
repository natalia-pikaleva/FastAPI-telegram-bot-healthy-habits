import logging
from fastapi import Depends
from telebot.types import Message
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_user_by_chat_id
import requests
from bot.keyboards.reply.core import habits_commands
from config import setup_logging, API_HOST
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["start"])
def bot_start(message: Message) -> None:
    """
    Функция получает на входе команду start и реализует кнопки меню с командами
    """
    logger.info("Start bot_start")
    with SessionLocal() as db:
        user = get_user_by_chat_id(db, message.chat.id)
        if not user:
            response = requests.post(
                f"http://{API_HOST}:8000/auth/login",
                json={"telegram_id": message.chat.id}
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                bot.send_message(chat_id=message.chat.id, text="Вы успешно авторизованы!")
            else:
                bot.send_message(chat_id=message.chat.id, text="Ошибка аутентификации. Попробуйте позже.")
        else:
            bot.send_message(chat_id=message.chat.id, text="Прекрасный день, чтобы начать формировать новую привычку! Нажми Создать новую привычку или выбери привычку из ранее созданного списка", reply_markup=habits_commands())
