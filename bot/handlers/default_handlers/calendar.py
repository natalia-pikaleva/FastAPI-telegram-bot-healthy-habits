import json
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from bot.keyboards.reply.core import habits_commands
from config import API_HOST, redis_client as redis
import logging
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from ...keyboards.inline.core import habit_fields_inline

logger = logging.getLogger(__name__)
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def calendar_callback(call):
    """
    Пользователь нажал на кнопку в календаре. Если он выбрал дату, то
    направляем запрос на соответствующий эндпоинт - обновление ранее созданной
    привычки или создание новой в зависимости от сохраненного состояния
    """
    logger.debug("Start calendar_callback")
    name, action, year, month, day = call.data.split(calendar_1.sep)
    date = calendar.calendar_query_handler(bot, call, name, action, year, month, day)
    chat_id = call.from_user.id
    saved_action = redis.hget(f"data_chat_id:{chat_id}", "action")

    if action == 'DAY':
        with SessionLocal() as db:
            token = get_token_for_user(db, chat_id)
        if not token:
            bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
            return

        if saved_action == "create_set_date_at":

            # Формируем данные для отправки на FastAPI
            title = redis.hget(f"data_chat_id:{chat_id}", "title")
            repeat_period = redis.hget(f"data_chat_id:{chat_id}", "repeat_period")
            week_days = redis.hget(f"data_chat_id:{chat_id}", "week_days")
            if not week_days is None:
                week_days = json.loads(week_days)

            habit_payload = {
                "title": title,
                "repeat_period": repeat_period,
                "week_days": week_days,
                "start_at": date.isoformat()
            }

            # Отправка POST-запроса на FastAPI сервер
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"http://{API_HOST}:8000/habits/create", json=habit_payload, headers=headers)

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

                # Очистка данных пользователя, оставляем только id текущей отображаемой привычки
                redis.delete(f"data_chat_id:{chat_id}")
                redis.hset(f"data_chat_id:{chat_id}", "habit_id", data["id"])

                # Обработка успешного ответа
                bot.send_message(chat_id, "Привычка успешно добавлена", reply_markup=habit_fields_inline(data))
            else:
                bot.send_message(chat_id, "Ошибка при выполнении запроса", reply_markup=habits_commands())

        if saved_action == "update":
            # Формируем данные для отправки на FastAPI
            habit_payload = {
                "start_at": date.isoformat(),
            }

            habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

            if habit_id is None:
                bot.send_message(chat_id, "Выберите привычку из списка", reply_markup=habits_commands())

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

                # Очистка данных пользователя, оставляем только id текущей отображаемой привычки
                redis.delete(f"data_chat_id:{chat_id}")
                redis.hset(f"data_chat_id:{chat_id}", "habit_id", data["id"])

                # Обработка успешного ответа
                bot.send_message(chat_id, "Привычка успешно обновлена", reply_markup=habit_fields_inline(data))
            else:
                bot.send_message(chat_id, "Ошибка при выполнении запроса", reply_markup=habits_commands())
    elif action == 'CANCEL':
        bot.send_message(chat_id, "Выбор даты отменён", reply_markup=habits_commands())
