from telebot import types


def habits_commands():
    """
    Функция реализует меню со списком команд для изменения или удаления привычки
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Обо мне")
    btn2 = types.KeyboardButton("Создать новую привычку")
    btn3 = types.KeyboardButton("Список всех привычек")
    btn4 = types.KeyboardButton("Установить время напоминания")

    markup.add(btn1, btn2, btn3, btn4)

    return markup
