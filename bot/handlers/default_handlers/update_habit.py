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
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')

user_selected_fields = defaultdict(set)


@bot.callback_query_handler(func=lambda call: call.data in ["title"])
def callback_update_title(call):
    user_id = call.from_user.id
    if user_id not in user_selected_habit:
        bot.send_message(user_id, "Выберите привычку из списка", reply_markup=habits_commands())

    msg = bot.send_message(user_id, "Вы хотите изменить название привычки? Введите новое название привычки. Для отмены нажмите Назад")
    bot.register_next_step_handler(msg, process_title_update)


def process_title_update(message):
    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return

    # Формируем данные для отправки на FastAPI
    habit_payload = {
        "title": message.text,
    }

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
        bot.send_message(message.chat.id, "Привычка успешно обновлена", reply_markup=habit_fields_inline(data))
    else:
        bot.send_message(message.chat.id, "Ошибка при выполнении запроса.")


@bot.callback_query_handler(func=lambda call: call.data in ["repeat_period"])
def callback_update_repeat_period(call):
    user_id = call.from_user.id
    if user_id not in user_selected_habit:
        bot.send_message(user_id, "Выберите привычку из списка", reply_markup=habits_commands())

    if not 'action' in user_data[user_id]:
        user_data[user_id] = {'action': "update"}
    else:
        user_data[user_id]['action'] = "update"

    bot.send_message(user_id, "Выберите периодичность", reply_markup=set_repeat_period_inline())




@bot.callback_query_handler(func=lambda call: call.data in ["start_at"])
def callback_update_start_at(call):
    user_id = call.from_user.id
    user_data[user_id] = {'action': "update"}

    if user_id not in user_selected_habit:
        bot.send_message(user_id, "Выберите привычку из списка", reply_markup=habits_commands())

    if not 'action' in user_data[user_id]:
        user_data[user_id] = {'action': "update"}
    else:
        user_data[user_id]['action'] = "update"

    now = datetime.datetime.now()
    markup = calendar.create_calendar(name=calendar_1.prefix, year=now.year, month=now.month)
    bot.send_message(user_id, "Выберите дату:", reply_markup=markup)
