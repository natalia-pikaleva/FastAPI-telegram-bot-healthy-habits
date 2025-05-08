from telebot import types


def create_menu():
    """
    Функция реализует меню с командами бота
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Обо мне")
    btn2 = types.KeyboardButton("Найти информацию о фильме/сериале")
    btn3 = types.KeyboardButton("Найти фильм/сериал по рейтингу")
    btn4 = types.KeyboardButton("Найти фильм/сериал с низким бюджетом")
    btn5 = types.KeyboardButton("Найти фильм/сериал с высоким бюджетом")
    btn6 = types.KeyboardButton("Просмотр истории запросов")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    markup.add(btn5)
    markup.add(btn6)

    return markup


def auth_menu():
    """
    Функция реализует меню с командами бота
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Обо мне")
    btn2 = types.KeyboardButton("Ввести пароль")
    btn3 = types.KeyboardButton("Зарегистрироваться")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)

    return markup
