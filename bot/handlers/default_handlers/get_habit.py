from ...keyboards.inline.core import habit_fields_inline
from ...keyboards.reply.core import habits_commands
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST, redis_client as redis
import logging
from collections import defaultdict

setup_logging()
logger = logging.getLogger(__name__)

user_selected_habit = defaultdict(dict)


@bot.callback_query_handler(func=lambda call: call.data.startswith('habit_'))
def handle_habit_callback(call):
    """Пользователь нажал на привычку в списке, возвращаем пользователю данные о привычке
    в виде inline keyboard и сохраняем id привычки в словаре"""
    habit_id = int(call.data.split('_')[1])
    chat_id = call.from_user.id

    # Сохраняем id привычки
    redis.hset(f"data_chat_id:{chat_id}", "habit_id", habit_id)

    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://{API_HOST}:8000/habits/{habit_id}", headers=headers)

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
        bot.send_message(chat_id, "Чтобы изменить параметр привычки, нажмите на него",
                         reply_markup=habit_fields_inline(data, ""))
    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())
