from telebot import types


def create_menu():
    """
    Функция реализует меню с командами бота
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Обо мне")
    btn2 = types.KeyboardButton("Создать новую привычку")
    btn3 = types.KeyboardButton("Список всех привычек")
    btn4 = types.KeyboardButton("Команда4")
    btn5 = types.KeyboardButton("Команда5")
    btn6 = types.KeyboardButton("Команда6")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    markup.add(btn5)
    markup.add(btn6)

    return markup

def habits_commands():
    """
    Функция реализует меню со списком команд для изменения или удаления привычки
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Изменить привычку")
    markup.add(btn)
    btn = types.KeyboardButton("Удалить привычку")
    markup.add(btn)
    btn = types.KeyboardButton("Список всех привычек")
    markup.add(btn)

    return markup
