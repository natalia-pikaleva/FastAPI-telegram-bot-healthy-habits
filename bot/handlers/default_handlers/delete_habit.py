from telebot.types import Message
from ...keyboards.inline.core import confirmation_of_habit_deletion_inline
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
def callback_delete_habit_first_step(call):
    habit_id = int(call.data.split('_')[1])
    chat_id = call.from_user.id
    user_selected_habit[chat_id]["habit_id"] = habit_id
    if chat_id not in user_selected_habit:
        bot.send_message(chat_id, "Выберите привычку из списка", reply_markup=habits_commands())

    bot.send_message(chat_id, "Вы уверены, что хотите удалить привычку?",
                     reply_markup=confirmation_of_habit_deletion_inline())


@bot.callback_query_handler(func=lambda call: call.data.startswith('yes_delete'))
def callback_delete_habit_second_step(call):
    chat_id = call.from_user.id
    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    habit_id = user_selected_habit[chat_id]["habit_id"]

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"http://{API_HOST}:8000/habits/{habit_id}/delete", headers=headers)

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
        bot.send_message(chat_id, "Привычка удалена", reply_markup=habits_commands())
    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_delete'))
def callback_cancel(call):
    chat_id = call.from_user.id
    user_selected_habit[chat_id] = {}

    bot.send_message(chat_id, "Удаление отменено", reply_markup=habits_commands())
