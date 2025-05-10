from telebot.types import Message
from ...keyboards.inline.core import habit_list_inline
from ...keyboards.reply.core import habits_commands
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
import logging
from collections import defaultdict
from .get_habits import user_selected_habit

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(func=lambda message: message.text == "Удалить привычку")
def bot_delete_habit(message: Message) -> None:
    """
    Хендлер для удаления привычки
    """
    logger.info("Start bot_delete_habit")

    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return

    habit_id = user_selected_habit[message.chat.id]["habit_id"]

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"http://{API_HOST}:8000/habits/{habit_id}/delete", headers=headers)

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        auth_response = requests.post(
            f"http://{API_HOST}:8000/auth/login",
            json={"telegram_id": message.chat.id}
        )
        if auth_response.status_code == 200:
            new_token = auth_response.json().get("access_token")
            bot.send_message(message.chat.id, "Токен обновлён, повторите команду.")
        else:
            bot.send_message(message.chat.id, "Ошибка авторизации, попробуйте позже.")
        return

    if response.status_code == 200:
        data = response.json()
        # Обработка успешного ответа
        bot.send_message(message.chat.id, f"data: {data}")
    else:
        bot.send_message(message.chat.id, "Ошибка при выполнении запроса.")
