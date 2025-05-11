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
        if field != "id":
            if field == "start_at":
                value = value.split('T')[0]
            btn = types.InlineKeyboardButton(
                text=f"{field_names_dict[field]}: {value}",
                callback_data=field
            )
            markup.add(btn)
    btn = types.InlineKeyboardButton(
        text=f"Удалить привычку ❌",
        callback_data=f"delete_{data['id']}"
    )
    markup.add(btn)
    return markup

def set_repeat_period_inline():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(
        text="Ежедневно",
        callback_data="daily"
    )
    btn2 = types.InlineKeyboardButton(
        text="Еженедельно",
        callback_data="weekly"
    )

    markup.add(btn1, btn2)
    return markup
#
# def habit_update_fields_inline(selected_fields: set):
#     markup = types.InlineKeyboardMarkup(row_width=1)
#
#     def btn_text(field_name, display_text):
#         return f"✅ {display_text}" if field_name in selected_fields else display_text
#
#     btn1 = types.InlineKeyboardButton(
#         text=btn_text("title", "Название привычки"),
#         callback_data="title"
#     )
#     btn2 = types.InlineKeyboardButton(
#         text=btn_text("repeat_period", "Периодичность"),
#         callback_data="repeat_period"
#     )
#     btn3 = types.InlineKeyboardButton(
#         text=btn_text("start_at", "Дата начала"),
#         callback_data="start_at"
#     )
#     btn4 = types.InlineKeyboardButton(
#         text="Далее",
#         callback_data="submit_update"
#     )
#     markup.add(btn1, btn2, btn3, btn4)
#     return markup
