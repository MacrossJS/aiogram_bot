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


def create_reply_kb():
    # Инициализируем билдер
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    # Создаем кнопки
    contact_btn: KeyboardButton = KeyboardButton(
        text=LEXICON_BTN['btn_phone'],
        request_contact=True)
    geo_btn: KeyboardButton = KeyboardButton(
        text=LEXICON_BTN['btn_geo'],
        request_location=True)
    # Создаем кнопку приложение
    web_app_btn: KeyboardButton = KeyboardButton(
        text=LEXICON_BTN['btn_web'],
        web_app=WebAppInfo(url="https://macrossjs.github.io/"))
    # Добавляем кнопки в билдер
    kb_builder.row(contact_btn, geo_btn, web_app_btn, width=1)
    # Создаем объект клавиатуры
    keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(resize_keyboard=True,
                                                         one_time_keyboard=True,
                                                         input_field_placeholder='Нажмите любую из кнопок')
    return keyboard
