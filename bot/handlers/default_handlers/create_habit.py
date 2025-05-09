import logging
from fastapi import Depends
from telebot.types import Message
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from bot.keyboards.reply.core import create_menu
from config import setup_logging, API_HOST
import logging

setup_logging()
logger = logging.getLogger(__name__)
user_data = {}


@bot.message_handler(func=lambda message: message.text == "Создать новую привычку")
def bot_create_habit(message: Message) -> None:
    """
    Хендлер для создания новой привыки
    """
    logger.info("Start bot_create_habit")

    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return

    bot.send_message(message.chat.id, "Введите название привычки:")
    bot.register_next_step_handler(message, process_name_step)


def process_name_step(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'title': message.text}
    bot.send_message(chat_id, "Введите периодичность (например, daily, weekly):")
    bot.register_next_step_handler(message, process_repeat_period_step)


def process_repeat_period_step(message):
    chat_id = message.chat.id
    user_data[chat_id]['repeat_period'] = message.text
    bot.send_message(chat_id, "Введите дату начала в формате ГГГГ-ММ-ДД (например, 2025-05-10):")
    bot.register_next_step_handler(message, process_start_at_step)


def process_start_at_step(message):
    chat_id = message.chat.id
    user_data[chat_id]['start_at'] = message.text

    # Здесь можно добавить валидацию даты

    # Формируем данные для отправки на FastAPI
    habit_payload = {
        "title": user_data[chat_id]['title'],
        "repeat_period": user_data[chat_id]['repeat_period'],
        "start_at": user_data[chat_id]['start_at']
    }

    # Отправка POST-запроса на ваш FastAPI сервер
    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"http://{API_HOST}:8000/habits/create", json=habit_payload, headers=headers)

    if response.status_code == 201:
        bot.send_message(chat_id, "Привычка успешно создана!")
    else:
        bot.send_message(chat_id, f"Ошибка при создании привычки: {response.text}")

    # Очистка данных пользователя
    user_data.pop(chat_id, None)

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
        bot.send_message(message.chat.id, f"Данные: {data}")
    # else:
    #     bot.send_message(message.chat.id, "Ошибка при выполнении запроса.")
