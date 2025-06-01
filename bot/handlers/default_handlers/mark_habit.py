from ...keyboards.inline.core import habit_fields_inline, habit_list_inline
from ...keyboards.reply.core import habits_commands
from ...setup import bot
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST
import logging

setup_logging()
logger = logging.getLogger(__name__)


@bot.callback_query_handler(func=lambda call: call.data.startswith('mark_'))
def callback_mark_habit(call):
    chat_id = call.from_user.id

    habit_id = int(call.data.split('_')[1])

    type_answer = call.data.split('_')[2]

    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(chat_id, "Пожалуйста, авторизуйтесь через /start", reply_markup=habits_commands())
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"http://{API_HOST}:8000/habits/{habit_id}/mark",
                             headers=headers)

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

        if type_answer == "one":  # если тип ответа one - надо вернуть пользователю информацию об одной привычке
            data = response.json()

            # Обработка успешного ответа
            bot.send_message(chat_id,
                             "Отметка о выполнении проставлена/снята",
                             reply_markup=habit_fields_inline(data))

        elif type_answer == "list":  # если тип ответа list - надо вернуть пользователю список всех привычек
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
                bot.send_message(chat_id, "Список ваших привычек:",
                                 reply_markup=habit_list_inline(data, "list"))
            else:
                bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())

        elif type_answer == "unmarkedlist":
            # если тип ответа unmarkedlist - надо вернуть пользователю список всех не выполненных сегодня привычек
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"http://{API_HOST}:8000/habits/unmarked", headers=headers)

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
                bot.send_message(chat_id, "Список привычек без отметок о выполнении за сегодня:",
                                 reply_markup=habit_list_inline(data, "unmarkedlist"))
            else:
                bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())
    else:
        bot.send_message(chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands())
