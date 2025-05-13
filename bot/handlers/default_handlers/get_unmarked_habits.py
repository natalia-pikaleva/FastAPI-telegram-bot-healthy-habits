from telebot.types import Message
from ...keyboards.inline.core import habit_list_inline
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["unmarked_habits"])
@bot.message_handler(func=lambda message: message.text == "Список привычек без отметки")
def bot_get_unmarked_habits(message: Message) -> None:
    """
    Хендлер для получения списка не выполненных привычек
    """
    logger.info("Start bot_get_unmarked_habits")

    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://{API_HOST}:8000/habits/unmarked", headers=headers)

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
        if data == []:
            bot.send_message(message.chat.id, "За сегодня все привычки выполнены! Так держать!")

        else:
            bot.send_message(message.chat.id, "Список привычек без отметок о выполнении за сегодня:", reply_markup=habit_list_inline(data, "unmarkedlist"))
    else:
        bot.send_message(message.chat.id, "Ошибка при выполнении запроса.")
