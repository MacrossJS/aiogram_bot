from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from lexicon.lexicon import *


# Функция для формирования инлайн-клавиатуры на лету
def create_inline_kb(width: int, *args: str, go_exit: str | None = None, **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []
    # Заполняем список кнопками из аргументов args и kwargs
    for button in args:
        buttons.append(InlineKeyboardButton(
            text=LEXICON.get(button, button), callback_data=button))
    for button, text in kwargs.items():
        buttons.append(InlineKeyboardButton(text=text, callback_data=button))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)
    # Добавляем в билдер последнюю кнопку, если она передана в функцию
    if go_exit:
        kb_builder.row(InlineKeyboardButton(text='🔙Назад', callback_data=go_exit))
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


