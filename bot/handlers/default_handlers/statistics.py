from telebot.types import Message
from ...keyboards.inline.core import statistics_habit_list_inline
from ...keyboards.reply.core import habits_commands
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["statistics"])
@bot.message_handler(func=lambda message: message.text == "Статистика")
def bot_get_statistics(message: Message) -> None:
    """
    Хендлер для просмотра статистики
    """
    logger.info("Start bot_create_habit")
    chat_id = message.chat.id
    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://{API_HOST}:8000/habits/statistics", headers=headers)

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        auth_response = requests.post(
            f"http://{API_HOST}:8000/auth/login",
            json={"telegram_id": chat_id}
        )
        if auth_response.status_code == 200:
            new_token = auth_response.json().get("access_token")
            bot.send_message(chat_id, "Токен обновлён, повторите команду.", reply_markup=habits_commands())
        else:
            bot.send_message(chat_id, "Ошибка авторизации, попробуйте позже.", reply_markup=habits_commands())
        return

    if response.status_code == 200:
        data = response.json()
        # Обработка успешного ответа
        if len(data) > 0:
            bot.send_message(chat_id, "Статистика за последнюю неделю:",
                         reply_markup=statistics_habit_list_inline(data))
        else:
            bot.send_message(chat_id, "Похоже, вы не создали ни одной привычки. Самое время начать!", reply_markup=habits_commands())

    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())


@bot.callback_query_handler(func=lambda call: call.data.startswith('habitstatistics_'))
def handle_statistics_habit_callback(call):
    """Пользователь нажал на привычку в списке, возвращаем пользователю статистику за 21 день"""
    habit_id = int(call.data.split('_')[1])

    chat_id = call.from_user.id
    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://{API_HOST}:8000/habits/{habit_id}/statistics", headers=headers)

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        auth_response = requests.post(
            f"http://{API_HOST}:8000/auth/login",
            json={"telegram_id": chat_id}
        )
        if auth_response.status_code == 200:
            new_token = auth_response.json().get("access_token")
            bot.send_message(chat_id, "Токен обновлён, повторите команду.", reply_markup=habits_commands())
        else:
            bot.send_message(chat_id, "Ошибка авторизации, попробуйте позже.", reply_markup=habits_commands())
        return

    if response.status_code == 200:
        data = response.json()
        # Обработка успешного ответа
        bot.send_message(chat_id, f"Статистика за 21 день - привычка {data["title"]}", reply_markup=habits_commands())
        bot.send_message(chat_id, f"{data["tracker"]}", reply_markup=habits_commands())

    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())
