from telebot import types

field_names_dict = {"title": "Название",
                    "repeat_period": "Периодичность",
                    "start_at": "Дата начала"}

week_days = {0: "пн",
             1: "вт",
             2: "ср",
             3: "чт",
             4: "пт",
             5: "сб",
             6: "вс"}

def habit_list_inline(data, type_answer):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for habit in data:
        btn1 = types.InlineKeyboardButton(
            text=habit["title"],
            callback_data=f"habit_{habit['id']}"
        )
        if "today_mark" in habit and not habit["today_mark"] is None:
            btn2 = types.InlineKeyboardButton(
                text="✅",
                callback_data=f"mark_{habit['id']}_{type_answer}"
            )
        else:
            btn2 = types.InlineKeyboardButton(
                text="🔲",
                callback_data=f"mark_{habit['id']}_{type_answer}"
            )
        buttons.append(btn1)
        buttons.append(btn2)

    markup.add(*buttons)
    return markup


def habit_fields_inline(data):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for field, value in data.items():
        if not field in ["id", "today_mark", "reminder_time", "week_days"]:
            if field == "start_at":
                value = value.split('T')[0]
            btn = types.InlineKeyboardButton(
                text=f"{field_names_dict[field]}: {value}",
                callback_data=field
            )
            markup.add(btn)
    if data.get("repeat_period") == "Еженедельно" and data.get("week_days") is not None:
        week_days_str = " ".join([week_days[day] for day in data["week_days"]])
        btn = types.InlineKeyboardButton(
            text=f"Дни недели: {week_days_str}",
            callback_data="weekly"
        )
        markup.add(btn)
    if "today_mark" in data and not data["today_mark"] is None:
        btn1 = types.InlineKeyboardButton(
            text="✅ Сегодня привычка выполнена",
            callback_data=f"mark_{data['id']}_one"
        )
    else:
        btn1 = types.InlineKeyboardButton(
            text="🔲 Привычка сегодня не выполнена",
            callback_data=f"mark_{data['id']}_one"
        )
    if data.get("reminder_time") is not None:
        btn2 = types.InlineKeyboardButton(
            text=f"Время напоминания: {data['reminder_time'][:-3]}",
            callback_data=f"setreminder_{data['id']}"
        )
    else:
        btn2 = types.InlineKeyboardButton(
            text="Установить время напоминания",
            callback_data=f"setreminder_{data['id']}"
        )
    btn3 = types.InlineKeyboardButton(
        text=f"Удалить привычку ❌",
        callback_data=f"delete_{data['id']}"
    )
    markup.add(btn1, btn2, btn3)

    return markup


def set_repeat_period_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(
        text="Ежедневно",
        callback_data="daily"
    )
    btn2 = types.InlineKeyboardButton(
        text="Еженедельно",
        callback_data="weekly"
    )

    markup.add(*[btn1, btn2])
    return markup


def hours_inline():
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    for hour in range(24):
        btn = types.InlineKeyboardButton(
            text=f"{hour:02d}:00",
            callback_data=f"hour_{hour}"
        )
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def timezone_inline():
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []

    for zone in range(13):
        btn = types.InlineKeyboardButton(
            text=f"UTC+{zone}",
            callback_data=f"timezone_-_{zone}"
        )
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def confirmation_of_habit_deletion_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(
        text="Удалить",
        callback_data="yes_delete"
    )
    btn2 = types.InlineKeyboardButton(
        text="Отмена",
        callback_data="cancel_delete"
    )

    markup.add(*[btn1, btn2])
    return markup


def confirmation_of_habit_update_inline():
    markup = types.InlineKeyboardMarkup(row_width=1)

    btn = types.InlineKeyboardButton(
        text="Отмена",
        callback_data="cancel_update"
    )

    markup.add(btn)
    return markup


def mark_habit(habit_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(
        text="Да",
        callback_data=f"mark_{habit_id}_one"
    )
    btn2 = types.InlineKeyboardButton(
        text="Нет",
        callback_data="cancel"
    )

    markup.add(*[btn1, btn2])
    return markup


def statistics_habit_list_inline(data):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for habit in data:
        btn1 = types.InlineKeyboardButton(
            text=habit["title"],
            callback_data=f"habitstatistics_{habit['id']}"
        )

        btn2 = types.InlineKeyboardButton(
            text=habit["week"],
            callback_data=f"habit_{habit['id']}"
        )

        buttons.append(btn1)
        buttons.append(btn2)

    markup.add(*buttons)
    return markup


def choose_week_days_inline(data):
    markup = types.InlineKeyboardMarkup(row_width=2)

    buttons = []
    for day in range(7):
        if day in data:
            btn = types.InlineKeyboardButton(
                text=f"✅ {week_days[day]}",
                callback_data=f"weekday_{day}"
            )
        else:
            btn = types.InlineKeyboardButton(
                text=f"{week_days[day]}",
                callback_data=f"weekday_{day}"
            )
        buttons.append(btn)
    btn = types.InlineKeyboardButton(
        text="Далее",
        callback_data="choose_week_days"
    )
    buttons.append(btn)
    markup.add(*buttons)
    return markup
