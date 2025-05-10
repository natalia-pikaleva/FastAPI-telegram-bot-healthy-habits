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