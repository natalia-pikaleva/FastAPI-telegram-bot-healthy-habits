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


@bot.callback_query_handler(func=lambda call: call.data in ["daily", "weekly"])
def callback_choose_repeat_period(call):
    chat_id = call.from_user.id

    # Если пользователь на данный момент редактирует ранее созданную привычку,
    # делаем запрос на изменение, возвращаем пользователю измененную привычку
    if user_data[chat_id]["action"] == "update":
        if chat_id not in user_selected_habit:
            bot.send_message(chat_id, "Выберите привычку из списка", reply_markup=habits_commands())
        # Формируем данные для отправки на FastAPI
        habit_payload = {
            "repeat_period": call.data,
        }

        habit_id = user_selected_habit[chat_id]["habit_id"]

        # Отправка POST-запроса на ваш FastAPI сервер
        with SessionLocal() as db:
            token = get_token_for_user(db, chat_id)
        if not token:
            bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
            return

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"http://{API_HOST}:8000/habits/{habit_id}/update", json=habit_payload,
                                 headers=headers)

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
            bot.send_message(chat_id, "Привычка успешно обновлена", reply_markup=habit_fields_inline(data, ""))
        else:
            bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())

    # Если пользователь на данный момент создает новую привычку,
    # фиксируем в словаре периодичность и направляем на следующий этап - выбор даты начала
    if user_data[chat_id]["action"] == "create":
        user_data[chat_id]['repeat_period'] = call.data
        now = datetime.datetime.now()
        markup = calendar.create_calendar(name=calendar_1.prefix, year=now.year, month=now.month)
        bot.send_message(chat_id, "Выберите дату:", reply_markup=markup)
