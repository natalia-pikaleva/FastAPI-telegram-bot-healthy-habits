from ...keyboards.inline.core import habit_fields_inline, set_repeat_period_inline
from ...keyboards.reply.core import habits_commands
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
import logging
from collections import defaultdict
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime
from .get_habit import user_selected_habit
from .create_habit import user_data

setup_logging()
logger = logging.getLogger(__name__)


@bot.callback_query_handler(func=lambda call: call.data.startswith('mark_'))
def callback_mark_habit(call):
    chat_id = call.from_user.id

    habit_id = int(call.data.split('_')[1])

    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start")
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"http://{API_HOST}:8000/habits/{habit_id}/mark",
                             headers=headers)

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        auth_response = requests.post(
            f"http://{API_HOST}:8000/auth/login",
            json={"telegram_id": chat_id}
        )
        if auth_response.status_code == 200:
            new_token = auth_response.json().get("access_token")
            bot.send_message(chat_id, "Токен обновлён, повторите команду.")
        else:
            bot.send_message(chat_id, "Ошибка авторизации, попробуйте позже.")
        return

    if response.status_code == 200:
        data = response.json()
        # Обработка успешного ответа
        bot.send_message(chat_id, "Отметка о выполнении проставлена/снята", reply_markup=habit_fields_inline(data))
    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.")
