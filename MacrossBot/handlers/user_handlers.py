import os
from os.path import getctime
import json
from datetime import datetime

from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from keyboards.keyboard_builder import create_inline_kb

from lexicon.lexicon import *

router: Router = Router()

team = [250, 352, 301, 225, 351, 247, 268, 283, 288, 269, 363, 371, 447, 387, 388, 222]


def time_now():
    """Получим текущее время с учетом ОС"""
    return datetime.today().strftime('%H:%M:%S')


def log(user, log_text):
    """Сформируем вывод красивого лога
    цвет + текущее время + имя бота"""
    color = 90 + user.id % 10
    user_info = f"{user.first_name} {user.last_name if user.last_name else ''} | @{user.username} ({user.id})"
    print(f"\033[{color}m{time_now()}: [{user_info}] --> {log_text}")


def get_logs_list():
    """Получим список лог-файлов"""
    log_list = os.listdir(f'logs/')
    return sorted(log_list)


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


@router.message(CommandStart())
async def process_start_command(message: Message):
    user = message.from_user
    log(user, 'Запустил бота')
    await message.answer(
        text=LEXICON['/start'].format(message.from_user.first_name),
        parse_mode="HTML",
        reply_markup=create_inline_kb(3, top_all=LEXICON_BTN['top_all'],
                                      progress=LEXICON_BTN['progress'],
                                      top_stats=LEXICON_BTN['top_stats'],
                                      top_rep=LEXICON_BTN['top_rep'],
                                      dayly_tokyo=LEXICON_BTN['dayly'],
                                      maps_sewerage_1=LEXICON_BTN['maps']))


@router.callback_query(Text(text='top_all'))
async def process_top_all(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, LEXICON_BTN['top_all'])
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
                                     reply_markup=create_inline_kb(3, X=LEXICON_BTN['top_all'],
                                                                   progress=LEXICON_BTN['progress'],
                                                                   top_stats=LEXICON_BTN['top_stats'],
                                                                   top_rep=LEXICON_BTN['top_rep'],
                                                                   dayly_tokyo=LEXICON_BTN['dayly'],
                                                                   maps_sewerage_1=LEXICON_BTN['maps']))
    await callback.answer()


@router.callback_query(Text(text='progress'))
async def process_top_progress(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, LEXICON_BTN['progress'])
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
                                     reply_markup=create_inline_kb(3, top_all=LEXICON_BTN['top_all'],
                                                                   X=LEXICON_BTN['progress'],
                                                                   top_stats=LEXICON_BTN['top_stats'],
                                                                   top_rep=LEXICON_BTN['top_rep'],
                                                                   dayly_tokyo=LEXICON_BTN['dayly'],
                                                                   maps_sewerage_1=LEXICON_BTN['maps']))
    await callback.answer()


@router.callback_query(Text(text='top_stats'))
async def process_top_stats(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, LEXICON_BTN['top_stats'])
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
                                     reply_markup=create_inline_kb(3, top_all=LEXICON_BTN['top_all'],
                                                                   progress=LEXICON_BTN['progress'],
                                                                   X=LEXICON_BTN['top_stats'],
                                                                   top_rep=LEXICON_BTN['top_rep'],
                                                                   dayly_tokyo=LEXICON_BTN['dayly'],
                                                                   maps_sewerage_1=LEXICON_BTN['maps']))
    await callback.answer()


@router.callback_query(Text(text='top_rep'))
async def process_top_stats(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, LEXICON_BTN['top_rep'])
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
                                     reply_markup=create_inline_kb(3, top_all=LEXICON_BTN['top_all'],
                                                                   progress=LEXICON_BTN['progress'],
                                                                   top_stats=LEXICON_BTN['top_stats'],
                                                                   X=LEXICON_BTN['top_rep'],
                                                                   dayly_tokyo=LEXICON_BTN['dayly'],
                                                                   maps_sewerage_1=LEXICON_BTN['maps']))
    await callback.answer()


async def edit_message_with_media(message, way: int):
    if way:
        await message.answer_photo(photo=LEXICON_MEDIA['dayly_2024'], caption="Ежедневные квесты Tokyo",
                                   reply_markup=create_inline_kb(2, go_exit="go_exit", dayly_tokyo="🏰Токио",
                                                                 dayly_rim="Рим➡"))
    else:
        await message.answer_photo(photo=LEXICON_MEDIA['photo_sewerage_1'], caption="Канализация 1 этаж",
                                   reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                 maps_sewerage_1=LEXICON_BTN['maps_sewerage_1'],
                                                                 maps_sewerage_2=LEXICON_BTN['maps_sewerage_2'],
                                                                 maps_old_park="🗺Старый парк",
                                                                 maps_druids_forest="🗺Лес друидов"))


@router.callback_query(Text(text='dayly_tokyo'))
async def callback_handler(callback: CallbackQuery):
    if callback.message.photo:
        log(callback.from_user, LEXICON_BTN['dayly_tokyo'])
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON_MEDIA['dayly_2024'],
                                  caption='Ежедневные квесты Токио'),
            reply_markup=create_inline_kb(2, go_exit="go_exit", X="🏰Токио", dayly_rim="Рим➡"))
    else:
        log(callback.from_user, LEXICON_BTN['dayly'])
        await edit_message_with_media(callback.message, 1)
    await callback.answer()


@router.callback_query(Text(text='dayly_rim'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, LEXICON_BTN['dayly_rim'])
    if callback.message.photo:
        await callback.message.edit_media(media=InputMediaPhoto(media=LEXICON_MEDIA['dayly_rim'],
                                                                caption='Ежедневные квесты Рим'),
                                          reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                        dayly_tokyo="⬅Токио",
                                                                        dayly_rim_X="🏰Рим"))
    await callback.answer()


@router.callback_query(Text(text='go_exit'))
async def callback_handler(callback: CallbackQuery, bot: Bot):
    log(callback.from_user, 'Удалил собщение')
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)


@router.callback_query(Text(text='maps_sewerage_1'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, LEXICON_BTN['maps_sewerage_1'])
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON_MEDIA['photo_sewerage_1'], caption=LEXICON_BTN['maps_sewerage_1']),
            reply_markup=create_inline_kb(2, go_exit="go_exit", X=LEXICON_BTN['maps_sewerage_1'],
                                          maps_sewerage_2=LEXICON_BTN['maps_sewerage_2'], maps_old_park="🗺Старый парк",
                                          maps_druids_forest="🗺Лес друидов"))
    else:
        await edit_message_with_media(callback.message, 0)
    await callback.answer()


@router.callback_query(Text(text='maps_sewerage_2'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, LEXICON_BTN['maps_sewerage_2'])
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON_MEDIA['photo_sewerage_2'], caption=LEXICON_BTN['maps_sewerage_2']),
            reply_markup=create_inline_kb(2, go_exit="go_exit", maps_sewerage_1=LEXICON_BTN['maps_sewerage_1'],
                                          X=LEXICON_BTN['maps_sewerage_2'], maps_old_park="🗺Старый парк",
                                          maps_druids_forest="🗺Лес друидов"))


@router.callback_query(Text(text='maps_old_park'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, '🗺Старый парк')
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON_MEDIA['photo_old_park'], caption='Старый парк'),
            reply_markup=create_inline_kb(2, go_exit="go_exit", maps_sewerage_1=LEXICON_BTN['maps_sewerage_1'],
                                          maps_sewerage_2=LEXICON_BTN['maps_sewerage_2'], X="🗺Старый парк",
                                          maps_druids_forest="🗺Лес друидов"))


@router.callback_query(Text(text='maps_druids_forest'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, '🗺Лес друидов')
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON_MEDIA['photo_rework'], caption='Лес друидов'),
            reply_markup=create_inline_kb(2, go_exit="go_exit", maps_sewerage_1=LEXICON_BTN['maps_sewerage_1'],
                                          maps_sewerage_2=LEXICON_BTN['maps_sewerage_2'], maps_old_park="🗺Старый парк",
                                          X="🗺Лес друидов"))


@router.callback_query(Text(text='X'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, "Вы уже нажимали данную кнопку!")
    await callback.answer("Вы уже просматриваете данную вкладку!\nПовторное нажатие не требуется!")


@router.message(Command(commands='admins'))
async def process_admins_command(message: Message):
    admin_ids = {784724803: 'Macross',
                 360745755: 'Варвара',
                 1353171442: 'Егор',
                 5499224283: 'Андрей',
                 5499224282: 'Кто-то'}
    answer = ''
    for aid in admin_ids:
        answer += f'🤴 <a href="tg://user?id={aid}">{admin_ids[aid]}</a>\n'
    await message.answer(text=answer, parse_mode="HTML")
