from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram import F

from config_data.config import Config, load_config
from lexicon.lexicon_ru import LEXICON_RU

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo

config: Config = load_config()

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=config.tg_bot.token)
dp: Dispatcher = Dispatcher()

# Инициализируем билдер
kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

# Создаем кнопки
contact_btn: KeyboardButton = KeyboardButton(
    text=LEXICON_RU['b_phone'],
    request_contact=True)
geo_btn: KeyboardButton = KeyboardButton(
    text=LEXICON_RU['b_geo'],
    request_location=True)
poll_btn: KeyboardButton = KeyboardButton(
    text=LEXICON_RU['b_geo'],
    request_poll=KeyboardButtonPollType())

# Создаем кнопку
web_app_btn: KeyboardButton = KeyboardButton(
    text='Start Web App',
    web_app=WebAppInfo(url="https://macrossjs.github.io/"))

# Добавляем кнопки в билдер
kb_builder.row(contact_btn, geo_btn, poll_btn, web_app_btn, width=1)

# Создаем объект клавиатуры
keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(resize_keyboard=True,
                                                     one_time_keyboard=True,
                                                     input_field_placeholder='Нажмите кнопку Start Web App')


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text='Экспериментируем со специальными кнопками',
                         reply_markup=keyboard)

# Создаем кнопки
btn_1: KeyboardButton = KeyboardButton(text='Кнопка 1')
btn_2: KeyboardButton = KeyboardButton(text='Кнопка 2')

# Создаем объект клавиатуры
placeholder_exmpl_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                    keyboard=[[btn_1, btn_2]],
                                    resize_keyboard=True,
                                    input_field_placeholder='Нажмите кнопку 1')


# Этот хэндлер будет срабатывать на команду "/placeholder"
@dp.message(Command(commands='placeholder'))
async def process_placeholder_command(message: Message):
    await message.answer(text='Экспериментируем с полем placeholder',
                         reply_markup=placeholder_exmpl_kb)


# Этот хэндлер будет срабатывать на отправку боту контакта
@dp.message(F.contact)
async def process_contact_share(message: Message):
    msg = f'Кажется, пришел контакт\n' \
          f'Телефон: {message.contact.phone_number}\n' \
          f'ID: {message.contact.user_id}\n' \
          f'Имя: {message.contact.first_name}\n' \
          f'Фамилия: {message.contact.last_name}\n' \
          f'vcard: {message.contact.vcard}'
    print(message.contact)
    await message.answer(text=msg)


# Этот хэндлер будет срабатывать запуск приложения
@dp.message(F.web_app_data)
async def process_web_app_data(message: Message):
    msg = f"{message.web_app_data.data}"
    print(message.web_app_data)
    await message.answer(text=msg)


# Этот хэндлер будет срабатывать на отправку геоданных
@dp.message(F.location)
async def process_location(message: Message):
    msg = f'Долгота: {message.location.longitude}\nШирота: {message.location.latitude}'
    print(msg)
    await message.answer(text=msg)


if __name__ == '__main__':
    dp.run_polling(bot)
