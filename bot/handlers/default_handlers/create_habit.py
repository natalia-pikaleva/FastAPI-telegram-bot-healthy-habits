from telebot.types import Message
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
from config import setup_logging
import logging
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime
from collections import defaultdict
from ...keyboards.inline.core import set_repeat_period_inline

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')

setup_logging()
logger = logging.getLogger(__name__)
user_data = defaultdict(dict)


@bot.message_handler(commands=["create_habit"])
@bot.message_handler(func=lambda message: message.text == "Создать новую привычку")
def bot_create_habit(message: Message) -> None:
    """
    Хендлер для создания новой привычки
    """
    logger.info("Start bot_create_habit")

    with SessionLocal() as db:
        token = get_token_for_user(db, message.chat.id)
    if not token:
        bot.send_message(message.chat.id, "Пожалуйста, авторизуйтесь через /start")
        return
    if not 'action' in user_data[message.chat.id]:
        user_data[message.chat.id] = {'action': "create"}
    else:
        user_data[message.chat.id]['action'] = "create"
    bot.send_message(message.chat.id, "Введите название привычки:")
    bot.register_next_step_handler(message, process_name_step)


def process_name_step(message):
    chat_id = message.chat.id
    user_data[chat_id]['title'] = message.text
    bot.send_message(chat_id, "Выберите периодичность", reply_markup=set_repeat_period_inline())
