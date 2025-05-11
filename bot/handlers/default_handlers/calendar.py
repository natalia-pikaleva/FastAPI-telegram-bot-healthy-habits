from ...setup import bot
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime
from telebot.types import Message
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from bot.keyboards.reply.core import habits_commands
from config import setup_logging, API_HOST
import logging
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime
from collections import defaultdict
from .update_habit import user_selected_habit
from .create_habit import user_data
from ...keyboards.inline.core import habit_fields_inline

logger = logging.getLogger(__name__)
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def calendar_callback(call):
    logger.debug("Start calendar_callback")
    name, action, year, month, day = call.data.split(calendar_1.sep)
    date = calendar.calendar_query_handler(bot, call, name, action, year, month, day)
    chat_id = call.from_user.id
    if action == 'DAY':
        bot.send_message(call.from_user.id, f"Вы выбрали дату: {date.strftime('%d.%m.%Y')} - {date}")

        if user_data[call.from_user.id]["action"] == "create":
            logger.debug("Action is create")

            # Формируем данные для отправки на FastAPI
            habit_payload = {
                "title": user_data[chat_id]['title'],
                "repeat_period": user_data[chat_id]['repeat_period'],
                "start_at": date.isoformat()
            }

            # Отправка POST-запроса на ваш FastAPI сервер
            with SessionLocal() as db:
                token = get_token_for_user(db, chat_id)
            if not token:
                bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start")
                return

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"http://{API_HOST}:8000/habits/create", json=habit_payload, headers=headers)

            logger.debug(f"Status response: {response.status_code}")

            if response.status_code == 201:
                bot.send_message(chat_id, "Привычка успешно создана!", reply_markup=habits_commands())
            else:
                bot.send_message(chat_id, f"Ошибка при создании привычки: {response.text}")

            # Очистка данных пользователя
            user_data.pop(chat_id, None)

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
                bot.send_message(chat_id, f"Данные: {data}")
            # else:
            #     bot.send_message(message.chat.id, "Ошибка при выполнении запроса.")

        if user_data[call.from_user.id]["action"] == "update":
            with SessionLocal() as db:
                token = get_token_for_user(db, chat_id)
            if not token:
                bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start")
                return

            # Формируем данные для отправки на FastAPI
            habit_payload = {
                "start_at": date.isoformat(),
            }

            habit_id = user_selected_habit[chat_id]["habit_id"]

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
                    bot.send_message(chat_id, "Токен обновлён, повторите команду.")
                else:
                    bot.send_message(chat_id, "Ошибка авторизации, попробуйте позже.")
                return

            if response.status_code == 200:
                data = response.json()
                # Обработка успешного ответа
                bot.send_message(chat_id, "Привычка успешно обновлена", reply_markup=habit_fields_inline(data))
            else:
                bot.send_message(chat_id, "Ошибка при выполнении запроса.")
    elif action == 'CANCEL':
        bot.send_message(call.from_user.id, "Выбор даты отменён")
