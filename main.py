from bot.setup import bot
from database.db_init import start_bd
import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - " "%(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

app = FastAPI()


#
# import handlers
# from utils.set_bot_commands import set_default_commands
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    """
    Start BD
    """
    try:
        logger.debug("Start sratup_event function")
        # set_default_commands(bot)
        # bot.infinity_polling(none_stop=True)
        await start_bd()
    except Exception as e:
        logger.error(f"Error during function startup_event: {e}")
