import copy
import json
import os
from os.path import getctime
from datetime import datetime
from random import choice
import colorama as colorama
from aiogram import Dispatcher, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command, Text
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (CallbackQuery, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardMarkup, Message, BotCommand, InputMediaPhoto)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from config_data.config import Config, load_config

# from Tokyo_Users_statistic import *

# Загружаем конфиг в переменную config
config: Config = load_config()

colorama.init()

# Инициализируем бот
bot: Bot = Bot(token=config.tg_bot.token,
               parse_mode='HTML')
print(config.tg_bot.token)
dp: Dispatcher = Dispatcher()

ADMINS = config.tg_bot.admin_ids

# Инициализируем константу размера игрового поля
FIELD_SIZE: int = 8
ATTEMPT = 35

# Создаем словарь соответствий
LEXICON: dict = {
    '/start': 'Привет <b>{0}</b>!\nТут немного статистики по <b>New Tokyo - Online Game</b>',
    '/game': 'Привет <b>{0}</b>, вот твое поле. Найди все вражеские корабли!\nОдин <b>x4</b>, два <b>x3</b> и три'
             ' <b>x2</b>\nУ вас есть <b>{1}</b> выстрелов!',
    '/help': 'Данный бот является тестовой площадкой для изучения работы с телеграм API при помощи библиотеки aiogram'
             ' 3.0.0b7, может содержать ошибки и недоработки, а так же неожиданно полностью менять свое наполнение.',
    '/raiting': '<b>Список топ игроков:</b>\n\n',
    0: '___',
    1: '🌊',
    2: '💥',
    'miss': 'Мимо!',
    'hit': 'Попал!',
    'used': 'Вы уже стреляли сюда!',
    'next_move': 'Делайте ваш следующий ход!\nУ вас <b>{0}</b> выстрелов\nОсталось <b>{1}</b> врагов!',
    'loose': 'Увы, <b>{0}</b> но вы проиграли(=\nМожет еще попытку?',
    'win': '🎉<b>Ура, {0} - Победитель!</b>🎉\nВы справились за <b>{1}</b> попыток!',
    'photo_id1': 'AgACAgIAAxkBAAIPRWWA86CxsPXblsSptx12sHyNvnV-AAJB0jEbNDAISF99wPoT9X2_AQADAgADeQADMwQ',
    'photo_id2': 'AgACAgIAAxkBAAIPR2WA87Ez0Mb9ZejhPm9v69PG1ij3AAJC0jEbNDAISIPlFqIB3QXlAQADAgADeQADMwQ',
    'photo_sewerage_1': 'AgACAgIAAxkBAAIP4GWHFDJHdpM67xPn8Zj02BvR0GjnAAIq0jEbrKk5SIshTLvxMK5jAQADAgADeQADMwQ',
    'photo_sewerage_2': 'AgACAgIAAxkBAAIQAAFlhysdLJVv5FddLy-_MmonLh-5twACztIxG6ypOUixAhlart_u5wEAAwIAA3kAAzME',
    'photo_old_park': 'AgACAgIAAxkBAAIQCWWHQwAB_PsCCAAB-Kh3zkpMLqJyoRMAAsLYMRsfezhIIa-sdFw4dTkBAAMCAAN5AAMzBA',
    'photo_rework': 'AgACAgIAAxkBAAIP7WWHGP81u4g5dFST_MHdHlynVOUFAAJZ0jEbrKk5SHRWDE_fL3oWAQADAgADeQADMwQ'
}

LEXICON_BTN: dict[str, str] = {
    'btn_phone': '☎️Отправить номер',
    'btn_geo': '🌍 Отправить геолокацию',
    'btn_web': '🌐 Start Web App'}

LEXICON_COMMANDS2: dict[str, str] = {
    '/start': 'Tokyo Info',
    '/game': 'Морской бой',
    '/raiting': 'Топ лучших игроков',
    '/help': 'Справка по работе бота',
    '/admins': "Список админов"
}

# Хардкодим расположение кораблей на игровом поле
ships: list[list[int]] = [
    [1, 0, 1, 1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0]]

ships2: list[list[int]] = [
    [0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 1, 1]]

ships3: list[list[int]] = [
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 1, 1, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 1, 1, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0]]

ships4: list[list[int]] = [
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 1, 1],
    [0, 0, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0]]

ships5: list[list[int]] = [
    [0, 0, 0, 1, 1, 1, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1],
    [0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]]

ships_test: list[list[int]] = [
    [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]]

# Инициализируем "базу данных" пользователей
users_db = {}
folder = "database"
db_name = "tg_users_db"
team = [250, 352, 301, 225, 351, 247, 268, 283, 288, 269, 363, 371, 447, 387, 388, 222]


def time_now():
    """Получим текущее время с учетом ОС"""
    return datetime.today().strftime('%H:%M:%S')


def log(user, log_text):
    """Сформируем вывод красивого лога
    цвет + текущее время + имя бота"""
    color = 90 + user.id % 10
    user_info = f"{user.first_name} {user.last_name if user.last_name else ''} | @{user.username} ({user.id})"
    print(f"\033[{color}m{time_now()}: [{user_info}]\n--> {log_text}")


def load_from_json():
    """Восстановление словаря users посре рестарта"""
    global users_db
    if os.path.isfile(f'{folder}/{db_name}.json'):
        with open(f'{folder}/{db_name}.json', 'rb') as from_db:
            users_db = json.load(from_db, object_hook=lambda arr: {int(key) if key.isdigit()
                                                                   else key: arr[key] for key in arr})


def dump_in_json():
    """СОхранение словаря users_db в json-файл"""
    with open(f'{folder}/{db_name}.json', 'w') as save:
        json.dump(users_db, save)


def get_logs_list():
    """Получим список лог-файлов"""
    log_list = os.listdir(f'logs\\')
    return log_list


def load_last_file(file_last):
    """Загрузим инфо о профилях из json в словарь"""
    with open(f"logs/{file_last}", 'r', encoding='utf-8') as last_file:
        users_last = json.load(last_file)
    return users_last


def load_penult_file(file_penult):
    """Загрузим инфо о профилях из json в словарь"""
    with open(f"logs/{file_penult}", 'r', encoding='utf-8') as penult_file:
        users_penult = json.load(penult_file)
    return users_penult


def create_progress(users: dict, users_old: dict) -> dict:
    """Добавим в users параметры прироста опыта и побед за сутки"""
    for key in users:
        if key in users_old:
            users[key]['rise'] = users[key]['exp'] - users_old[key]['exp']
            users[key]['kills'] = users[key]['wins'] - users_old[key]['wins']
        else:
            users[key]['rise'] = users[key]['exp']
            users[key]['kills'] = users[key]['wins']
    return users


def create_progress_users(users, top=1):
    """Отсортируем профили по параметру роста опыта"""
    for key, value in sorted(users.items(), key=lambda x: -x[1]['rise']):
        icon = '🔝' if int(key) in team else ''
        print(f"{top}. {icon}{value['name']}[{value['level']}] ➡  +{value['rise']}⭐ +{value['kills']}⚔️")
        top += 1
        if value['rise'] < 100:
            break


# Создаем свой класс фабрики коллбэков, указывая префикс
# и структуру callback_data
class FieldCallbackFactory(CallbackData, prefix="user_field"):
    x: int
    y: int


# Функция, которая пересоздает новое поле для каждого игрока
def reset_field(user_id: int) -> None:
    users_db[user_id]['ships'] = copy.deepcopy(choice([ships, ships2, ships3, ships4, ships5]))
    # users_db[user_id]['ships'] = copy.deepcopy(ships_test)
    users_db[user_id]['field'] = [[0 for _ in range(FIELD_SIZE)]
                                  for _ in range(FIELD_SIZE)]
    users_db[user_id]['attempt'] = ATTEMPT
    users_db[user_id]['ships_count'] = sum([sum(ship) for ship in users_db[user_id]['ships']])
    users_db[user_id]['total_games'] += 1


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
        kb_builder.row(InlineKeyboardButton(text='🔙Назад', callback_data='go_exit'))
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


# Функция, генерирующая клавиатуру в зависимости от данных из
# матрицы ходов пользователя
def get_field_keyboard(user_id: int) -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []

    for i in range(FIELD_SIZE):
        array_buttons.append([])
        for j in range(FIELD_SIZE):
            array_buttons[i].append(InlineKeyboardButton(
                text=LEXICON[users_db[user_id]['field'][i][j]],
                callback_data=FieldCallbackFactory(x=i, y=j).pack()))

    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=array_buttons)
    return markup


# Этот хэндлер будет срабатывать на команду /start, записывать
# пользователя в "базу данных", обнулять игровое поле и отправлять
# пользователю сообщение с клавиатурой
@dp.message(CommandStart())
async def process_start_command(message: Message):
    user = message.from_user
    log(user, 'Запустил бота')
    await message.answer(
        text=LEXICON['/start'].format(message.from_user.first_name),
        parse_mode="HTML",
        reply_markup=create_inline_kb(3, top_all='🏆Топ',
                                      progress='📈Рост',
                                      top_stats='🧠Статы',
                                      top_rep='🔔Репутация',
                                      dayly_tokyo="🏰Дейлики",
                                      maps_sewerage_1="🗺Карты"))


@dp.callback_query(Text(text='top_all'))
async def process_top_all(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, 'Запросил 🏆Топ')
    users = load_last_file(logs_list[-1])
    users_old = load_penult_file(logs_list[-2])
    all_users: dict = create_progress(users, users_old)
    ctime = datetime.fromtimestamp(getctime(f"logs/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = f"📊Данные собраны {ctime} мск" \
             f"\n🔄Обновление данных раз в сутки!" \
             f"\n👥Всего игроков: {len(all_users)} (+{len(users) - len(users_old)}👤)" \
             f"\n\n🏆Топ-50 игроков Tokyo:\n\n"
    numb = 1
    for key, value in sorted(all_users.items(), key=lambda x: -x[1]['exp']):
        icon = '😎' if int(key) in team else ''
        answer += f"{numb}. {icon}<a href='https://3ze.ru/user/#{key}'>{value['name']}</a>[<b>{value['level']}</b>]" \
                  f" >> {value['wins']}⚔,  {value['exp']}⭐\n"
        numb += 1
        if numb > 50:
            break
    # print(answer, len(answer))
    await callback.message.edit_text(text=answer, parse_mode="HTML",
                                     reply_markup=create_inline_kb(3, X='🏆Топ',
                                                                   progress='📈Рост',
                                                                   top_stats='🧠Статы',
                                                                   top_rep='🔔Репутация',
                                                                   dayly_tokyo="🏰Дейлики",
                                                                   maps_sewerage_1="🗺Карты"))
    await callback.answer()


@dp.callback_query(Text(text='progress'))
async def process_top_progress(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, 'Запросил 📈Рост')
    users = load_last_file(logs_list[-1])
    users_old = load_penult_file(logs_list[-2])
    all_users: dict = create_progress(users, users_old)
    ctime = datetime.fromtimestamp(getctime(f"logs/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = f"📊Данные собраны {ctime} мск" \
             f"\n🔄Обновление данных раз в сутки!" \
             f"\n👥Всего игроков: {len(all_users)} (+{len(users) - len(users_old)}👤)" \
             f"\n\n📈Прирост опыта за сутки:\n\n"
    numb = 1
    for key, value in sorted(users.items(), key=lambda x: -x[1]['rise']):
        icon = '😎' if int(key) in team else ''
        answer += f"{numb}. {icon}<a href='https://3ze.ru/user/#{key}'>{value['name']}</a>[<b>{value['level']}</b>]" \
                  f" >> +{value['rise']}⭐,  +{value['kills']}⚔\n"
        numb += 1
        if value['rise'] < 50:
            break
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML",
                                     reply_markup=create_inline_kb(3, top_all='🏆Топ',
                                                                   X='📈Рост',
                                                                   top_stats='🧠Статы',
                                                                   top_rep='🔔Репутация',
                                                                   dayly_tokyo="🏰Дейлики",
                                                                   maps_sewerage_1="🗺Карты"))
    await callback.answer()


@dp.callback_query(Text(text='top_stats'))
async def process_top_stats(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, 'Запросил 🧠Статы')
    users = load_last_file(logs_list[-1])
    users_old = load_penult_file(logs_list[-2])
    ctime = datetime.fromtimestamp(getctime(f"logs/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = f"📊Данные собраны {ctime} мск" \
             f"\n🔄Обновление данных раз в сутки!" \
             f"\n👤Всего игроков: {len(users)} (+{len(users) - len(users_old)}👤)" \
             f"\n\n🧠Топ по сумме статов (💪-🤹‍♂-🧠-🕵️‍♂-❤)\n\n"
    numb = 1
    for key, value in sorted(users.items(), key=lambda x: -x[1]['sum_stats']):
        icon = '😎' if int(key) in team else ''
        answer += f"{numb}. {icon}<a href='https://3ze.ru/user/#{key}'>{value['name']}</a>[<b>{value['level']}</b>]" \
                  f" >> <b>{value['sum_stats']}</b> ({value['strength']}-{value['agility']}-{value['wisdom']}-" \
                  f"{value['intuition']}-{value['vitality']})\n"
        numb += 1
        if numb > 30:
            break
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML",
                                     reply_markup=create_inline_kb(3, top_all='🏆Топ',
                                                                   progress='📈Рост',
                                                                   X='🧠Статы',
                                                                   top_rep='🔔Репутация',
                                                                   dayly_tokyo="🏰Дейлики",
                                                                   maps_sewerage_1="🗺Карты"))
    await callback.answer()


@dp.callback_query(Text(text='top_rep'))
async def process_top_stats(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, 'Запросил 🔔Репутация')
    users = load_last_file(logs_list[-1])
    users_old = load_penult_file(logs_list[-2])
    ctime = datetime.fromtimestamp(getctime(f"logs/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = f"📊Данные собраны {ctime} мск" \
             f"\n🔄Обновление данных раз в сутки!" \
             f"\n👤Всего игроков: {len(users)} (+{len(users) - len(users_old)}👤)" \
             f"\n\n🔔Топ по сумме репутаций (NT🟢 + Mars🔴)\n\n"
    numb = 1
    for key, value in sorted(users.items(), key=lambda x: -x[1]['sum_rep']):
        icon = '😎' if int(key) in team else ''
        answer += f"{numb}. {icon}<a href='https://3ze.ru/user/#{key}'>{value['name']}</a>[<b>{value['level']}</b>]" \
                  f" >> <b>{value['sum_rep']}</b> ({value['rep_NT']} + {value['rep_Mars']})\n"
        numb += 1
        if value['sum_rep'] < 1:
            break
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML",
                                     reply_markup=create_inline_kb(3, top_all='🏆Топ',
                                                                   progress='📈Рост',
                                                                   top_stats='🧠Статы',
                                                                   X='🔔Репутация',
                                                                   dayly_tokyo="🏰Дейлики",
                                                                   maps_sewerage_1="🗺Карты"))
    await callback.answer()


async def edit_message_with_media(message, way: int):
    if way:
        await message.answer_photo(photo=LEXICON[f'photo_id1'], caption="Ежедневные квесты Tokyo",
                                   reply_markup=create_inline_kb(2, go_exit="go_exit", dayly_tokyo="🏰Токио",
                                                                 dayly_rim="Рим➡"))
    else:
        await message.answer_photo(photo=LEXICON[f'photo_sewerage_1'], caption="Канализация 1 этаж",
                                   reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                 maps_sewerage_1="🗺Канализация 1 этаж",
                                                                 maps_sewerage_2="🗺Канализация 2 этаж",
                                                                 maps_old_park="🗺Старый парк",
                                                                 maps_druids_forest="🗺Лес друидов"))


@dp.callback_query(Text(text='dayly_tokyo'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, '⬅Токио')
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON['photo_id1'],
                                  caption='Ежедневные квесты Токио'),
            reply_markup=create_inline_kb(2, go_exit="go_exit", dayly_tokyo_X="🏰Токио", dayly_rim="Рим➡"))
    else:
        await edit_message_with_media(callback.message, 1)
    await callback.answer()


@dp.callback_query(Text(text='dayly_rim'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, 'Рим➡')
    if callback.message.photo:
        await callback.message.edit_media(media=InputMediaPhoto(media=LEXICON['photo_id2'],
                                                                caption='Ежедневные квесты Рим'),
                                          reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                        dayly_tokyo="⬅Токио",
                                                                        dayly_rim_X="🏰Рим"))
    await callback.answer()


@dp.callback_query(Text(text='go_exit'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, 'Удалил собщение')
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)


@dp.callback_query(Text(text='maps_sewerage_1'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, 'Канализация 1 этаж')
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON['photo_sewerage_1'], caption='Канализация 1 этаж'),
            reply_markup=create_inline_kb(2, go_exit="go_exit", X="🗺Канализация 1 этаж",
                                          maps_sewerage_2="🗺Канализация 2 этаж", maps_old_park="🗺Старый парк",
                                          maps_druids_forest="🗺Лес друидов"))
    else:
        await edit_message_with_media(callback.message, 0)
    await callback.answer()


@dp.callback_query(Text(text='maps_sewerage_2'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, '🗺Канализация 2 этаж')
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON['photo_sewerage_2'], caption='Канализация 2 этаж'),
            reply_markup=create_inline_kb(2, go_exit="go_exit", maps_sewerage_1="🗺Канализация 1 этаж",
                                          X="🗺Канализация 2 этаж", maps_old_park="🗺Старый парк",
                                          maps_druids_forest="🗺Лес друидов"))


@dp.callback_query(Text(text='maps_old_park'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, '🗺Старый парк')
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON['photo_old_park'], caption='Старый парк'),
            reply_markup=create_inline_kb(2, go_exit="go_exit", maps_sewerage_1="🗺Канализация 1 этаж",
                                          maps_sewerage_2="🗺Канализация 2 этаж", X="🗺Старый парк",
                                          maps_druids_forest="🗺Лес друидов"))


@dp.callback_query(Text(text='maps_druids_forest'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, '🗺Лес друидов')
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON['photo_rework'], caption='Лес друидов'),
            reply_markup=create_inline_kb(2, go_exit="go_exit", maps_sewerage_1="🗺Канализация 1 этаж",
                                          maps_sewerage_2="🗺Канализация 2 этаж", maps_old_park="🗺Старый парк",
                                          X="🗺Лес друидов"))


@dp.callback_query(Text(text='X'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, "Вы уже нажимали данную кнопку!")
    await callback.answer("Вы уже просматриваете данную вкладку!\nПовторное нажатие не требуется!")


@dp.message(F.content_type.in_({'photo', 'audio', 'voice', 'video', 'document'}))
async def send_echo(message: Message):
    # print(message.json(indent=4, exclude_none=True))
    if message.photo:
        file_type, file_id, unique_id = "🖼 Изображение", message.photo[-1].file_id, message.photo[-1].file_unique_id
    elif message.video:
        file_type, file_id, unique_id = "🎬 Видео", message.video.file_id, message.video.file_unique_id
    elif message.audio:
        file_type, file_id, unique_id = "🎶 Аудио", message.audio.file_id, message.audio.file_unique_id
    elif message.document:
        file_type, file_id, unique_id = "📑 Документ", message.document.file_id, message.document.file_unique_id
    elif message.voice:
        file_type, file_id, unique_id = "📢 Голосовое сообщение", message.voice.file_id, message.voice.file_unique_id
    else:
        file_type, file_id, unique_id = "Неизвестно", None, None
    answer = f"Вы прислали: <b>{file_type}</b>\n\n<b>ID:</b> {file_id}\n\n<b>UNIQUE_ID:</b> {unique_id}"
    await message.answer(answer, parse_mode='HTML')


@dp.message(Command(commands='game'))
async def process_start_game(message: Message):
    user = message.from_user
    if user.id not in users_db:
        users_db[user.id] = {}
        log(user, 'Создал профиль в боте')
        users_db[user.id]['user_name'] = user.first_name or user.username
        users_db[user.id]['win'] = 0
        users_db[user.id]['total_games'] = 0
    reset_field(user.id)
    log(user, 'Начал новую игру')
    await message.answer(
        text=LEXICON['/game'].format(message.from_user.first_name, users_db[user.id]['attempt']),
        reply_markup=get_field_keyboard(user.id))


@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await set_main_menu(bot)
    await message.answer(LEXICON['/help'], reply_markup=create_reply_kb())


@dp.message(Command(commands='admins'))
async def process_admins_command(message: Message):
    answer = 'Список пользователей с админ доступом:\n'
    for uid in ADMINS:
        answer += f'😎 <a href="tg://user?id={uid}">{users_db.get(uid, {}).get("user_name", "Admin")}</a>\n'
    await message.answer(text=answer, parse_mode="HTML")


@dp.message(Command(commands='raiting'))
async def process_raiting_command(message: Message):
    dump_in_json()
    log(message.from_user, 'Запросил рейтинг')
    answer, numb = 'Список топ игроков в морской бой:\n\n', 1
    for uid in sorted(users_db, key=lambda x: (users_db[x]['total_games'] / (users_db[x]['win'] or 0.1),
                                               -users_db[x]['win'])):
        name = users_db[uid]["user_name"]
        win = users_db[uid]["win"]
        total = users_db[uid]["total_games"]
        answer += f'{numb}. 🤴 <a href="tg://user?id={uid}">{name}</a> win: {win}' \
                  f' из {total} ({round(win / total * 100, 1)}%)\n'
        numb += 1
    await message.answer(text=answer, parse_mode="HTML")


@dp.callback_query(Text(text='raiting'))
async def process_raiting_callback(callback: CallbackQuery):
    answer, numb = '', 1
    for uid in sorted(users_db, key=lambda x: (users_db[x]['total_games'] / (users_db[x]['win'] or 0.1),
                                               -users_db[x]['win'])):
        name = users_db[uid]["user_name"]
        win = users_db[uid]["win"]
        total = users_db[uid]["total_games"]
        answer += f'{numb}. 🤴 <a href="tg://user?id={uid}">{name}</a> win: {win}' \
                  f' из {total} ({round(win / total * 100, 1)}%)\n'
        numb += 1
    return await callback.message.edit_text(
        text=LEXICON['/raiting'] + answer,
        parse_mode="HTML",
        reply_markup=create_inline_kb(1, again='Еще раунд!'))


@dp.callback_query(Text(text='again'))
async def process_play_again(callback: CallbackQuery):
    user = callback.from_user
    reset_field(user.id)
    return await callback.message.edit_text(
        text=LEXICON['/start'].format(user.first_name, users_db[user.id]['attempt']),
        reply_markup=get_field_keyboard(user.id))


@dp.callback_query(Text(text='wtf'))
async def process_more_buttons(callback: CallbackQuery):
    user = callback.from_user
    reset_field(user.id)
    return await callback.message.edit_text(
        text=LEXICON['/start'].format(user.first_name, users_db[user.id]['attempt']),
        reply_markup=get_field_keyboard(user.id))


# Этот хэндлер будет срабатывать на нажатие любой инлайн-кнопки на поле,
# запускать логику проверки результата нажатия и формирования ответа
@dp.callback_query(FieldCallbackFactory.filter())
async def process_category_press(callback: CallbackQuery,
                                 callback_data: FieldCallbackFactory):
    user = callback.from_user
    field = users_db[user.id]['field']
    ships = users_db[user.id]['ships']
    ships_count = users_db[user.id]['ships_count']
    users_db[user.id]['attempt'] -= 1
    attempt = users_db[user.id]['attempt']

    if attempt == 0:
        log(user, 'Проиграл боту')
        reset_field(user.id)
        return await callback.message.edit_text(
            text=LEXICON['loose'].format(user.first_name),
            reply_markup=get_field_keyboard(user.id))
    elif field[callback_data.x][callback_data.y] == 0 and \
            ships[callback_data.x][callback_data.y] == 0:
        answer = LEXICON['miss']
        field[callback_data.x][callback_data.y] = 1
    elif field[callback_data.x][callback_data.y] == 0 and \
            ships[callback_data.x][callback_data.y] == 1:
        answer = LEXICON['hit']
        field[callback_data.x][callback_data.y] = 2
    else:
        answer = LEXICON['used']

    field_count = sum([ship.count(2) for ship in field])
    if ships_count - field_count == 0:
        users_db[user.id]['win'] += 1
        log(user, f'Победил за {ATTEMPT - attempt} попыток!')
        return await callback.message.edit_text(
            text=LEXICON['win'].format(user.first_name, ATTEMPT - attempt),
            reply_markup=create_inline_kb(1, again='Повторим?!',
                                          raiting='Рейтинг',
                                          wtf='Больше кнопок!'))

    try:
        await callback.message.edit_text(
            text=LEXICON['next_move'].format(attempt, ships_count - field_count),
            reply_markup=get_field_keyboard(user.id), parse_mode='HTML')
    except TelegramBadRequest:
        pass

    await callback.answer(answer)


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


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
          description in LEXICON_COMMANDS2.items()]
    print("Команды установлены")
    await bot.set_my_commands(main_menu_commands)


if __name__ == '__main__':
    load_from_json()
    dp.run_polling(bot)
