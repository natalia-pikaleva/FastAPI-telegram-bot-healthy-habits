from ...keyboards.reply.core import habits_commands
from telebot.types import Message
from ...setup import bot
from config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda message: message.text == "😊 Обо мне")
def bot_help(message: Message) -> None:
    """
    Функция получает на входе команду help и возвращает пользователю справку
    """
    bot.send_message(chat_id=message.chat.id,
                     text="Я бот-помощник для трекинга привычек. Создавай привычки, "
                          "устанавливай удобное время напоминания и отмечай выполненные!\n\n"
                          "Чтобы закрепить привычку продержись 21 день подряд. "
                          "Для отслеживания твоих успехов воспользуйся кнопкой Статистика.\n\n"
                          "Если захочешь изменить привычку, "
                          "нажми на привычку в списке и нажми на параметр, "
                          "который хочешь изменить",
                     reply_markup=habits_commands())
