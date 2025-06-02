import json
from bot.keyboards.inline.core import habit_fields_inline, choose_week_days_inline
from bot.keyboards.reply.core import habits_commands
from bot.setup import bot
from bot.utils import get_new_token
from database.db_init import SessionLocal
from database.db_utils import get_token_for_user
import requests
from config import setup_logging, API_HOST, redis_client as redis
import logging
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime

setup_logging()
logger = logging.getLogger(__name__)
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")


def update_habit_repeat_period_daily_request_api(chat_id):
    """Формируем запрос на API для установки периодичности Ежедневно и возвращаем
    пользователю созданную привычку в виде инлайн кнопок"""
    redis.hset(f"data_chat_id:{chat_id}", "action", "update")

    # Проверяем, что пользователь выбрал привычку для редактирования
    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    if habit_id is None:
        bot.send_message(
            chat_id, "Выберите привычку из списка", reply_markup=habits_commands()
        )

    # Формируем данные для отправки на FastAPI
    habit_payload = {
        "repeat_period": "daily",
    }

    # Проверяем наличие токена
    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(
            chat_id,
            "Пожалуйста, авторизуйтесь через /start",
            reply_markup=habits_commands(),
        )
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"http://{API_HOST}:8000/habits/{habit_id}/update",
        json=habit_payload,
        headers=headers,
    )

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        get_new_token(chat_id)

    if response.status_code == 200:
        # Удаляем все данные кроме id привычки
        all_fields = redis.hkeys(f"data_chat_id:{chat_id}")
        all_fields = [
            field.decode() if isinstance(field, bytes) else field
            for field in all_fields
        ]
        fields_to_delete = [field for field in all_fields if field != "habit_id"]

        if fields_to_delete:
            redis.hdel(f"data_chat_id:{chat_id}", *fields_to_delete)

        data = response.json()
        # Обработка успешного ответа
        bot.send_message(
            chat_id,
            "Привычка успешно обновлена",
            reply_markup=habit_fields_inline(data),
        )
    else:
        bot.send_message(
            chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands()
        )


def update_habit_repeat_period_weekly_request_api(chat_id, week_days):
    """Формируем запрос на API для установки периодичности Еженедельно с указанием дней и возвращаем
    пользователю созданную привычку в виде инлайн кнопок"""
    redis.hset(f"data_chat_id:{chat_id}", "action", "update")

    # Проверяем, что пользователь выбрал привычку для редактирования
    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    if habit_id is None:
        bot.send_message(
            chat_id, "Выберите привычку из списка", reply_markup=habits_commands()
        )

    # Формируем данные для отправки на FastAPI
    habit_payload = {"repeat_period": "weekly", "week_days": week_days}

    with SessionLocal() as db:
        token = get_token_for_user(db, chat_id)
    if not token:
        bot.send_message(
            chat_id,
            "Пожалуйста, авторизуйтесь через /start",
            reply_markup=habits_commands(),
        )
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"http://{API_HOST}:8000/habits/{habit_id}/update",
        json=habit_payload,
        headers=headers,
    )

    if response.status_code == 401:
        # Токен истёк или недействителен, пробуем получить новый
        get_new_token(chat_id)

    if response.status_code == 200:
        data = response.json()

        # Удаляем все данные кроме id привычки
        all_fields = redis.hkeys(f"data_chat_id:{chat_id}")
        all_fields = [
            field.decode() if isinstance(field, bytes) else field
            for field in all_fields
        ]
        fields_to_delete = [field for field in all_fields if field != "habit_id"]

        if fields_to_delete:
            redis.hdel(f"data_chat_id:{chat_id}", *fields_to_delete)

        # Обработка успешного ответа
        bot.send_message(
            chat_id,
            "Привычка успешно обновлена",
            reply_markup=habit_fields_inline(data),
        )
    else:
        bot.send_message(
            chat_id, "Ошибка при выполнении запроса.", reply_markup=habits_commands()
        )


@bot.callback_query_handler(func=lambda call: call.data == "daily")
def callback_choose_repeat_period_daily(call):
    """
    Пользователь выбрал периодичность привычки Ежедневно.
    Если на данный момент пользователь редактирует привычку, направляем запрос
    на эндпоинт, если создает новую привычку, сохраняем периодичность и направляем на следующий шаг
    """
    chat_id = call.from_user.id

    # Проверяем действие на данный момент: если действие не создать новую привычку,
    # значит пользователь редактирует ранее созданную, устанавливаем поле действия update и
    # направляем запрос на API
    action = redis.hget(f"data_chat_id:{chat_id}", "action")
    if not action == "create_set_repeat_period":
        update_habit_repeat_period_daily_request_api(chat_id)

    # Если пользователь на данный момент создает новую привычку,
    # фиксируем в данных пользователя периодичность и направляем на следующий этап - выбор даты начала
    if action == "create_set_repeat_period":
        redis.hset(f"data_chat_id:{chat_id}", "repeat_period", call.data)
        redis.hset(f"data_chat_id:{chat_id}", "action", "create_set_date_at")
        now = datetime.datetime.now()
        markup = calendar.create_calendar(
            name=calendar_1.prefix, year=now.year, month=now.month
        )
        bot.send_message(chat_id, "Выберите дату:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "weekly")
def callback_choose_period_weekly(call):
    """Пользователь выбрал периодичность привычки Еженедельно.
    Сохраняем периодичность в данных пользователя и предлагаем выбрать дни недели"""
    chat_id = call.from_user.id

    # Проверяем, что пользователь выбрал привычку для редактирования
    habit_id = redis.hget(f"data_chat_id:{chat_id}", "habit_id")

    if habit_id is None:
        bot.send_message(
            chat_id, "Выберите привычку из списка", reply_markup=habits_commands()
        )

    redis.hset(f"data_chat_id:{chat_id}", "repeat_period", "weekly")

    # Если ранее были сохранены дни недели, берем этот список,
    # если еще не выбраны дни недели, передаем пустой список
    data = redis.hget(f"data_chat_id:{chat_id}", "week_days")
    if data is None:
        data = list()
    else:
        data = json.loads(data)

    bot.send_message(
        chat_id, "Выберите дни недели", reply_markup=choose_week_days_inline(data)
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("weekday_"))
def callback_choose_week_days(call):
    """
    Пользователь выбрал день недели - сохраняем в данных пользователя
    """
    chat_id = call.from_user.id

    day = int(call.data.split("_")[1])

    # Если ранее не был сохранен список дней недели, создаем пустой список,
    # если список уже создан, берем его и обновляем
    data = redis.hget(f"data_chat_id:{chat_id}", "week_days")
    if data is None:
        data = list()
    else:
        data = json.loads(data)

    # Если день недели есть в списке, удаляем его, если нет - добавляем
    if day in data:
        data.remove(day)
    else:
        data.append(day)

    redis.hset(f"data_chat_id:{chat_id}", "week_days", json.dumps(data))
    bot.send_message(
        chat_id, "Выберите дни недели", reply_markup=choose_week_days_inline(data)
    )


@bot.callback_query_handler(func=lambda call: call.data == "choose_week_days")
def callback_set_week_days(call):
    """
    Пользователь выбрал дни недели и нажал кнопку Далее.
    Проверяем, что хотя бы один день недели выбран.
    Если на данный момент пользователь редактирует привычку, направляем запрос
    на эндпоинт, если создает новую привычку, сохраняем данные и направляем на следующий шаг
    """
    chat_id = call.from_user.id

    data = redis.hget(f"data_chat_id:{chat_id}", "week_days")

    if data is None:
        bot.send_message(
            chat_id,
            "Выберите хотя бы один день недели и нажмите Далее",
            reply_markup=choose_week_days_inline([]),
        )

    week_days = sorted(json.loads(data))

    # Если пользователь на данный момент редактирует ранее созданную привычку,
    # делаем запрос на изменение, возвращаем пользователю измененную привычку
    action = redis.hget(f"data_chat_id:{chat_id}", "action")
    if not action == "create_set_repeat_period":
        update_habit_repeat_period_weekly_request_api(
            chat_id=chat_id, week_days=week_days
        )

    # Если пользователь на данный момент создает новую привычку,
    # фиксируем в redis дни недели и направляем далее
    if action == "create_set_repeat_period":
        redis.hset(f"data_chat_id:{chat_id}", "week_days", json.dumps(week_days))
        redis.hset(f"data_chat_id:{chat_id}", "action", "create_set_date_at")

        now = datetime.datetime.now()
        markup = calendar.create_calendar(
            name=calendar_1.prefix, year=now.year, month=now.month
        )
        bot.send_message(chat_id, "Выберите дату:", reply_markup=markup)
