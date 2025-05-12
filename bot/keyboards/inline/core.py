from telebot import types


def habit_list_inline(data):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for habit in data:
        btn = types.InlineKeyboardButton(
            text=habit["title"],
            callback_data=f"habit_{habit['id']}"
        )
        markup.add(btn)
    return markup


field_names_dict = {"title": "Название",
                    "repeat_period": "Периодичность",
                    "start_at": "Дата начала"}


def habit_fields_inline(data):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for field, value in data.items():
        if not field in ["id", "today_mark"]:
            if field == "start_at":
                value = value.split('T')[0]
            btn = types.InlineKeyboardButton(
                text=f"{field_names_dict[field]}: {value}",
                callback_data=field
            )
            markup.add(btn)
    if data["today_mark"]:
        btn1 = types.InlineKeyboardButton(
            text=f"✅ Сегодня привычка выполнена",
            callback_data=f"mark_{data['id']}"
        )
    else:
        btn1 = types.InlineKeyboardButton(
            text=f"🔲 Привычка еще не выполнена",
            callback_data=f"mark_{data['id']}"
        )
    btn2 = types.InlineKeyboardButton(
        text=f"Удалить привычку ❌",
        callback_data=f"delete_{data['id']}"
    )
    markup.add(btn1, btn2)
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
        callback_data="cancel"
    )

    markup.add(*[btn1, btn2])
    return markup
