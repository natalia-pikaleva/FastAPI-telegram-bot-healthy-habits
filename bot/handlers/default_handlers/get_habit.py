from ...keyboards.inline.core import habit_fields_inline
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
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
    user_selected_habit[call.from_user.id]["habit_id"] = habit_id

    with SessionLocal() as db:
        token = get_token_for_user(db, call.from_user.id)
    if not token:
        bot.send_message(call.from_user.id, "Пожалуйста, авторизуйтесь через /start")
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://{API_HOST}:8000/habits/{habit_id}", headers=headers)

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        auth_response = requests.post(
            f"http://{API_HOST}:8000/auth/login",
            json={"telegram_id": call.from_user.id}
        )
        if auth_response.status_code == 200:
            new_token = auth_response.json().get("access_token")
            bot.send_message(call.from_user.id, "Токен обновлён, повторите команду.")
        else:
            bot.send_message(call.from_user.id, "Ошибка авторизации, попробуйте позже.")
        return

    if response.status_code == 200:
        data = response.json()
        # Обработка успешного ответа
        bot.send_message(call.from_user.id, "Чтобы изменить параметр привычки, нажмите на него",
                         reply_markup=habit_fields_inline(data, "one"))
    else:
        bot.send_message(call.from_user.id, "Ошибка при выполнении запроса.")
