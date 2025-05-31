from telebot.types import Message
from ...setup import bot
from config import setup_logging, redis_client as redis, EXIT_COMMANDS
import logging
from collections import defaultdict
from ...keyboards.inline.core import set_repeat_period_inline



setup_logging()
logger = logging.getLogger(__name__)
user_data = defaultdict(dict)


@bot.message_handler(commands=["create_habit"])
@bot.message_handler(func=lambda message: message.text == "✍️ Создать новую привычку")
def bot_create_habit(message: Message) -> None:
    """
    Пользователь нажал на кнопку Создать новую привычку, проверяем наличие словаря для
    хранения данных, сохраняем действие Создать, предлагаем ввести название привычки
    """
    logger.info("Start bot_create_habit")
    chat_id = message.chat.id
    action = redis.hget(f"data_chat_id:{chat_id}", "action")

    # Сохраняем в redis действие Создать
    redis.hset(f"data_chat_id:{chat_id}", "action", "create_set_title")

    bot.send_message(chat_id, "Введите название привычки:")
    bot.register_next_step_handler(message, process_name_step)


def process_name_step(message):
    """Сохраняем название новой привычки, направляем пользователя на следующий шаг"""
    chat_id = message.chat.id

    # Если пользователь нажал любую кнопку меню
    if message.text in EXIT_COMMANDS:
        bot.send_message(chat_id, "Отмена создания привычки. Повторите команду")
        return

    action = redis.hget(f"data_chat_id:{chat_id}", "action")

    if action == "create_set_title":
        # Сохраняем в redis название привычки
        redis.hset(f"data_chat_id:{chat_id}", "title", message.text)
        redis.hset(f"data_chat_id:{chat_id}", "action", "create_set_repeat_period")
        bot.send_message(chat_id, "Выберите периодичность", reply_markup=set_repeat_period_inline())
    else:
        bot.send_message(chat_id, "Не понимаю команду")