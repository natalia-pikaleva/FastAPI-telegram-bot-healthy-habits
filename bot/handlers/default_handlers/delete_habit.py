from bot.keyboards.inline.core import confirmation_of_habit_deletion_inline
from bot.keyboards.reply.core import habits_commands
from bot.setup import bot
from bot.utils import get_new_token
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST, redis_client as redis
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def callback_delete_habit_first_step(call):
    habit_id = int(call.data.split("_")[1])
    chat_id = call.from_user.id

    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(
            chat_id,
            "Пожалуйста, авторизуйтесь через /start",
            reply_markup=habits_commands(),
        )
        return

    # Сохраняем id привычки
    redis.hset(f"data_chat_id:{chat_id}", "habit_id", habit_id)

    bot.send_message(
        chat_id,
        "Вы уверены, что хотите удалить привычку?",
        reply_markup=confirmation_of_habit_deletion_inline(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("yes_delete"))
def callback_delete_habit_second_step(call):
    chat_id = call.from_user.id

    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(
            chat_id,
            "Пожалуйста, авторизуйтесь через /start",
            reply_markup=habits_commands(),
        )
        return

    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"http://{API_HOST}:8000/habits/{habit_id}/delete", headers=headers
    )

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        get_new_token(chat_id)

    if response.status_code == 200:
        # Обработка успешного ответа
        bot.send_message(chat_id, "Привычка удалена", reply_markup=habits_commands())
    else:
        bot.send_message(
            chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands()
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_delete"))
def callback_cancel(call):
    chat_id = call.from_user.id

    bot.send_message(chat_id, "Удаление отменено", reply_markup=habits_commands())
