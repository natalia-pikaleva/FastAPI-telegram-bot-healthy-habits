from telebot.types import BotCommand
from config import DEFAULT_COMMANDS, API_HOST
from bot.setup import bot
import requests
from bot.keyboards.reply.core import habits_commands

def set_default_commands(bot):
    bot.set_my_commands([BotCommand(*i) for i in DEFAULT_COMMANDS])

def get_new_token(chat_id):
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
