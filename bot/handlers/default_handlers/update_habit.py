from ...keyboards.inline.core import habit_fields_inline, set_repeat_period_inline, confirmation_of_habit_update_inline
from ...keyboards.reply.core import habits_commands
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST, redis_client as redis, EXIT_COMMANDS
import logging
from collections import defaultdict
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime

setup_logging()
logger = logging.getLogger(__name__)
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')


@bot.callback_query_handler(func=lambda call: call.data == "title")
def callback_update_title(call):
    chat_id = call.from_user.id

    # Проверяем, что пользователь выбрал привычку для редактирования
    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    if habit_id is None:
        bot.send_message(chat_id, "Выберите привычку из списка", reply_markup=habits_commands())

    msg = bot.send_message(
        chat_id,
        "Вы хотите изменить название привычки? Введите новое название привычки",
        reply_markup=confirmation_of_habit_update_inline())
    bot.register_next_step_handler(msg, process_title_update)


def process_title_update(message):
    chat_id = message.chat.id

    # Если пользователь нажал любую кнопку меню
    if message.text in EXIT_COMMANDS:
        bot.send_message(chat_id, "Отмена изменения названия привычки. Повторите команду")
        return

        # Если пользователь нажал Отмена, id привычки не будет сохранено
    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    if habit_id is None:
        bot.send_message(chat_id, "Пожалуйста, повторите команду", reply_markup=habits_commands())

    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    # Формируем данные для отправки на FastAPI
    habit_payload = {
        "title": message.text,
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"http://{API_HOST}:8000/habits/{habit_id}/update", json=habit_payload, headers=headers)

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

        # Удаляем все данные кроме id привычки
        all_fields = redis.hkeys(f"data_chat_id:{chat_id}")
        all_fields = [field.decode() if isinstance(field, bytes) else field for field in all_fields]
        fields_to_delete = [field for field in all_fields if field != "habit_id"]

        if fields_to_delete:
            redis.hdel(f"data_chat_id:{chat_id}", *fields_to_delete)

        # Обработка успешного ответа
        bot.send_message(chat_id, "Привычка успешно обновлена", reply_markup=habit_fields_inline(data))
    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())


@bot.callback_query_handler(func=lambda call: call.data == "repeat_period")
def callback_update_repeat_period(call):
    chat_id = call.from_user.id

    # Проверяем, что пользователь выбрал привычку для редактирования
    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    if habit_id is None:
        bot.send_message(chat_id, "Выберите привычку из списка", reply_markup=habits_commands())

    # Проверяем, что пользователь не создает новую привычку
    action = redis.hget(f"data_chat_id:{chat_id}", "action")

    if not action == "create":
        redis.hset(f"data_chat_id:{chat_id}", "action", "update")

        bot.send_message(chat_id, "Выберите периодичность", reply_markup=set_repeat_period_inline())


@bot.callback_query_handler(func=lambda call: call.data == "start_at")
def callback_update_start_at(call):
    chat_id = call.from_user.id

    # Проверяем, что пользователь выбрал привычку для редактирования
    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    if habit_id is None:
        bot.send_message(chat_id, "Выберите привычку из списка", reply_markup=habits_commands())

    # Проверяем, что пользователь не создает новую привычку
    action = redis.hget(f"data_chat_id:{chat_id}", "action")

    if not action == "create":
        redis.hset(f"data_chat_id:{chat_id}", "action", "update")

        now = datetime.datetime.now()
        markup = calendar.create_calendar(name=calendar_1.prefix, year=now.year, month=now.month)
        bot.send_message(chat_id, "Выберите дату:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_update'))
def callback_cancel(call):
    chat_id = call.from_user.id

    # Удаляем все данные кроме id привычки
    all_fields = redis.hkeys(f"data_chat_id:{chat_id}")
    all_fields = [field.decode() if isinstance(field, bytes) else field for field in all_fields]
    fields_to_delete = [field for field in all_fields if field != "habit_id"]

    if fields_to_delete:
        redis.hdel(f"data_chat_id:{chat_id}", *fields_to_delete)

    bot.send_message(chat_id, "Изменение отменено", reply_markup=habits_commands())
