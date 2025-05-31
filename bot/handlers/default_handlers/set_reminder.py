from ...setup import bot
from database.db_init import SessionLocal
import requests
from bot.keyboards.reply.core import habits_commands
from bot.keyboards.inline.core import timezone_inline, hours_inline
from config import setup_logging, API_HOST, redis_client as redis
import logging
from database.db_utils import get_token_for_user

setup_logging()
logger = logging.getLogger(__name__)


@bot.callback_query_handler(func=lambda call: call.data.startswith('setreminder_'))
def bot_set_reminder_to_habit(call):
    """
    Хендлер для установки времени напоминания для конкретной привычки
    """
    chat_id = call.from_user.id

    habit_id = int(call.data.split('_')[1])

    # Сохраняем id привычки
    redis.hset(f"data_chat_id:{chat_id}", "habit_id", habit_id)

    bot.send_message(chat_id, "Выберите удобное время для напоминаний", reply_markup=hours_inline())


@bot.callback_query_handler(func=lambda call: call.data.startswith('hour_'))
def handle_set_hour_callback(call):
    """Пользователь выбрал время для напоминания, сохраняем время и предлагаем выбрать часовой пояс"""
    hour = int(call.data.split('_')[1])
    chat_id = call.from_user.id

    # Сохраняем выбранное время напоминания
    redis.hset(f"data_chat_id:{chat_id}", "hour", f"{hour:02d}:00")

    bot.send_message(chat_id, "Выберите ваш часовой пояс", reply_markup=timezone_inline())


@bot.callback_query_handler(func=lambda call: call.data.startswith('timezone_'))
def handle_set_timezone_callback(call):
    """Пользователь выбрал часовой пояс, сохраняем его в словаре и направляем запрос на эндпоинт"""
    sign = call.data.split('_')[1]
    zone = call.data.split('_')[2]

    timezone = f"Etc/GMT{sign}{zone}"
    chat_id = call.from_user.id

    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    # Формируем данные для отправки на FastAPI
    hour = redis.hget(f"data_chat_id:{chat_id}", "hour")
    reminder_payload = {
        "chat_id": chat_id,
        "time": hour,
        "timezone": timezone,
    }

    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"http://{API_HOST}:8000/habits/{habit_id}/set_reminder",
        json=reminder_payload,
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
        # Обработка успешного ответа
        bot.send_message(chat_id, f"Время напоминания установлено: {hour}",
                         reply_markup=habits_commands())
    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())
