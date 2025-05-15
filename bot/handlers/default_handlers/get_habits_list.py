from telebot.types import Message
from ...keyboards.inline.core import habit_list_inline
from ...keyboards.reply.core import habits_commands
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["habits_list"])
@bot.message_handler(func=lambda message: message.text == "Список всех привычек")
def bot_get_habits(message: Message) -> None:
    """
    Хендлер для просмотра всех привычек
    """
    logger.info("Start bot_create_habit")
    chat_id = message.chat.id
    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://{API_HOST}:8000/habits", headers=headers)
    logger.debug(f'Headers: {response.request.headers}')
    logger.debug(f'Code: {response.status_code}')

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
        bot.send_message(chat_id, "Список ваших привычек (с отметками о выполнении за сегодня):", reply_markup=habit_list_inline(data, "list"))
    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())
