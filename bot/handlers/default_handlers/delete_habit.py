from telebot.types import Message
from ...keyboards.inline.core import habit_list_inline
from ...keyboards.reply.core import habits_commands
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
import logging
from collections import defaultdict
from .get_habit import user_selected_habit

setup_logging()
logger = logging.getLogger(__name__)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def callback_update_repeat_period(call):
    habit_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    user_selected_habit[user_id]["habit_id"] = habit_id
    if user_id not in user_selected_habit:
        bot.send_message(user_id, "Выберите привычку из списка", reply_markup=habits_commands())

    msg = bot.send_message(user_id, "Вы уверены, что хотите удалить привычку? Что удалить введите 1")
    bot.register_next_step_handler(msg, process_habit_delete)


def process_habit_delete(message):
    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return

    if message.text != "1":
        return

    habit_id = user_selected_habit[message.chat.id]["habit_id"]
    bot.send_message(message.chat.id, f"Сейчас сохранена привычка с id: {user_selected_habit[message.chat.id]["habit_id"]}")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"http://{API_HOST}:8000/habits/{habit_id}/delete", headers=headers)

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
        bot.send_message(message.chat.id, "Привычка удалена", reply_markup=habits_commands())
    else:
        bot.send_message(message.chat.id, "Ошибка при выполнении запроса.")
