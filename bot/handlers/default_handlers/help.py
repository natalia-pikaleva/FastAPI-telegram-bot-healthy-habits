from ...keyboards.reply.core import habits_commands
from telebot.types import Message
from ...setup import bot
from config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["help"])
def bot_help(message: Message) -> None:
    """
    Функция получает на входе команду help и возвращает пользователю справку
    """
    bot.send_message(chat_id=message.chat.id, text="Справка о работе бота", reply_markup=habits_commands())

    # TODO написать информацию о работе бота