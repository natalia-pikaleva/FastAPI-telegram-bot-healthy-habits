from telebot.types import Message
from bot.keyboards.inline.core import habit_list_inline
from bot.keyboards.reply.core import habits_commands
from bot.setup import bot
from bot.utils import get_new_token
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["unmarked_habits"])
@bot.message_handler(func=lambda message: message.text == "⚪️ Привычки без отметки")
def bot_get_unmarked_habits(message: Message) -> None:
    """
    Хендлер для получения списка не выполненных привычек
    """
    logger.info("Start bot_get_unmarked_habits")
    chat_id = message.chat.id
    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://{API_HOST}:8000/habits/unmarked", headers=headers)

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        get_new_token(chat_id)

    if response.status_code == 200:
        data = response.json()
        # Обработка успешного ответа
        if len(data) == 0:
            bot.send_message(chat_id, "За сегодня все привычки выполнены! Так держать!", reply_markup=habits_commands())

        else:
            bot.send_message(chat_id, "Список привычек без отметок о выполнении за сегодня:",
                             reply_markup=habit_list_inline(data, "unmarkedlist"))
    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())
