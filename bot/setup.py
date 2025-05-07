import config
from telebot import TeleBot
from telebot.storage import StateMemoryStorage


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)