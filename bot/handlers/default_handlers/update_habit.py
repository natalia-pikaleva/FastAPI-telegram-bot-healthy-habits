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


@bot.message_handler(func=lambda message: message.text == "Изменить привычку")
def bot_update_habit(message: Message) -> None:
    """
    Хендлер для изменения привычки
    """
    logger.info("Start bot_update_habit")

    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return

    bot.send_message(message.chat.id, "Введите название привычки:")
    bot.register_next_step_handler(message, process_name_step)


def process_name_step(message):
    # TODO реализовать возможность пользователю изменить только отдельные поля привычки, а не все
    chat_id = message.chat.id
    user_selected_habit[message.chat.id]["title"] = message.text
    bot.send_message(chat_id, "Введите периодичность (например, daily, weekly):")
    bot.register_next_step_handler(message, process_repeat_period_step)


def process_repeat_period_step(message):
    chat_id = message.chat.id
    user_selected_habit[message.chat.id]["repeat_period"] = message.text
    bot.send_message(chat_id, "Введите дату начала в формате ГГГГ-ММ-ДД (например, 2025-05-10):")
    bot.register_next_step_handler(message, process_start_at_step)


def process_start_at_step(message):
    chat_id = message.chat.id
    user_selected_habit[message.chat.id]["start_at"] = message.text
    # Здесь можно добавить валидацию даты

    # Формируем данные для отправки на FastAPI
    habit_payload = {
        "title": user_selected_habit[message.chat.id]["title"],
        "repeat_period": user_selected_habit[message.chat.id]["repeat_period"],
        "start_at": user_selected_habit[message.chat.id]["start_at"]
    }

    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return

    habit_id = user_selected_habit[message.chat.id]["habit_id"]

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"http://{API_HOST}:8000/habits/{habit_id}/update", json=habit_payload, headers=headers)

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
