import os
from os.path import getctime
import json
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import CallbackQuery, Message
from keyboards.keyboard_builder import create_inline_kb

from lexicon.lexicon_forest import *
from services.forest_bosses import *
from services.forest_keys import *
from services.forest_alchemy import *

router: Router = Router()


def time_now():
    """Получим текущее время с учетом ОС"""
    return datetime.today().strftime('%H:%M:%S')


def log(user: CallbackQuery | Message, log_text: str) -> None:
    """Сформируем вывод красивого лога: цвет + текущее время + имя бота"""
    color = 90 + user.from_user.id % 10
    user_info = f"{user.from_user.first_name} {user.from_user.last_name or ''} | @{user.from_user.username or '-'} " \
                f"({user.from_user.id})"
    if isinstance(user, CallbackQuery):
        chat = user.message.chat
    else:
        chat = user.chat

    if chat.type == 'private':
        print(f"\033[{color}m{time_now()}: [{user_info}] --> {log_text}\033[0m")
    else:
        chat_name = chat.title or "Чат"
        print(f"\033[{color}m{time_now()}: [{chat_name}]>[{user_info}] --> {log_text}\033[0m")


def get_logs_list(path: str):
    """Получим список лог-файлов"""
    log_list = os.listdir(f'logs_forest/{path}/')
    return sorted(log_list)


def get_clans_list():
    """Получим список стай/кланов"""
    clans_list = os.listdir(f'logs_forest/')
    return clans_list


def load_log_file(log_path):
    """Загрузим инфо о последнем из json в словарь"""
    with open(log_path, 'r', encoding='utf-8') as last_file:
        logs = json.load(last_file)
    return logs


def save_info(users_db: dict) -> None:
    """Сохраним в json-файл"""
    with open(f"database/users_db.json", 'w', encoding='utf-8') as save:
        json.dump(users_db, save, indent=4, ensure_ascii=False)


def create_progress(users: dict, users_old: dict) -> dict:
    """Добавим в users параметры прироста опыта и побед за сутки"""
    for key in users:
        if key in users_old:
            users[key]['exp_gain'] = users[key]['exp'] - users_old[key]['exp']
            # users[key]['rating_change'] = users[key]['rating'] - users_old[key]['rating']
            # users[key]['position_change'] = users[key]['position'] - users_old[key]['position']
        else:
            users[key]['exp_gain'] = 0
            # users[key]['rating_shift'] = 0
            # users[key]['position_shift'] = 0
    return users


@router.callback_query(Text(text='start_forest'))
async def process_start_command(callback: CallbackQuery):
    user = callback.from_user.first_name
    users_db = load_log_file("database/users_db.json")
    if str(callback.from_user.id) in users_db:
        user = f"{users_db[str(callback.from_user.id)]['icon']}{users_db[str(callback.from_user.id)]['game_name']}"
    await callback.message.edit_text(
        text=FOREST_LEXICON['start_forest'].format(user),
        parse_mode="HTML",
        reply_markup=create_inline_kb(
            2, forest_bosses=FOREST_BTN['forest_bosses'],
            forest_keys=FOREST_BTN['forest_keys'],
            forest_commands=FOREST_BTN['forest_commands'],
            forest_alchemy_1=FOREST_BTN['forest_alchemy'],
            clan_statistic=FOREST_BTN['clan_statistic'],
            calc_build_0=FOREST_BTN['calc_build'],
        ))


@router.callback_query(Text(text='clan_statistic'))
async def forest_commands(callback: CallbackQuery):
    clan_list = get_clans_list()
    buttons = {f"clan_{name}_2": name for name in clan_list}
    await callback.message.edit_text(
        text="📈Для обновления данных по вашей стае или добавления ее в бота"
             " перешлите сюда(в ЛС бота) сообщение из игры со списком участников стаи.\n\n"
             f"⚙️Для удаления данных своей стаи из бота свяжитесь с разработчиком --> "
             f"<a href='tg://user?id=784724803'><b>Macross</b></a> / "
             f"<a href='tg://user?id=1660983940'><b>Baka-Baka</b></a>\n"
        ,
        parse_mode="HTML",
        reply_markup=create_inline_kb(
            2, go_exit="start_forest", **buttons,
        ))


@router.callback_query(Text(text='forest_commands'))
async def forest_commands(callback: CallbackQuery):
    await callback.message.edit_text(
        text=forest_command,
        parse_mode="HTML",
        reply_markup=create_inline_kb(
            1, go_exit="start_forest"
        ))


@router.callback_query(lambda callback: callback.data.startswith('calc_build_'))
async def calc_build(callback: CallbackQuery):
    user = callback.from_user
    user_id = str(user.id)
    log(callback, f"{FOREST_BTN['calc_build']}")
    calc_lvl = callback.data.split('_')[-1]
    users_db = load_log_file("database/users_db.json")
    if user_id not in users_db or users_db[user_id]['forest_class'] is None:
        msg_text = f"{user.first_name}, выберите свой класс:"
        kb = create_inline_kb(1, 'blade_master', 'forest_protector', 'night_hunter', go_exit="start_forest")
    else:
        msg_text = f"{users_db[user_id]['game_name']}, ваш класс {FOREST_BTN[users_db[user_id]['forest_class']]}\n\n" \
                   f"⚙️Калькулятор находится в разработке, загляните позже."
        kb = create_inline_kb(1, go_exit="start_forest")
    await callback.message.edit_text(
        text=msg_text,
        parse_mode="HTML",
        reply_markup=kb)


@router.callback_query(Text(text=['blade_master', 'forest_protector', 'night_hunter']))
async def choise_user_class(callback: CallbackQuery):
    user = callback.from_user
    user_id = str(user.id)
    user_class = callback.data
    users_db = load_log_file("database/users_db.json")
    log(callback, f"выбрал класс {user_class}")
    if user_id not in users_db:
        users_db[user_id] = {
            'game_name': user.first_name,
            'forest_class': user_class,
            'icon': FOREST_BTN[user_class][0]
        }
    users_db[user_id]['forest_class'] = user_class

    save_info(users_db)

    await callback.message.edit_text(
        text=f"{users_db[user_id]['icon']}{users_db[user_id]['game_name']}, "
             f"Ваш основной класс записан как {FOREST_BTN[user_class]}",
        parse_mode="HTML",
        reply_markup=create_inline_kb(
            1, go_exit="calc_build_"
        ))


@router.callback_query(lambda callback: callback.data.startswith('forest_alchemy_'))
async def forest_alchemy(callback: CallbackQuery):
    alchemy_lvl = callback.data.split('_')[-1]

    if callback.message.text == globals()[f"alchemy_{alchemy_lvl}"]:
        await callback.answer()
        log(callback, f"Дебил нажал повторно {alchemy_lvl}")
        return
    log(callback, f"Рецепты зелий лвл {alchemy_lvl}")
    await callback.message.edit_text(
        text=globals()[f"alchemy_{alchemy_lvl}"],
        parse_mode="HTML",
        reply_markup=create_inline_kb(5, 'forest_alchemy_1', 'forest_alchemy_2', 'forest_alchemy_3', 'forest_alchemy_4',
                                      'forest_alchemy_5', go_exit="start_forest",
                                      ))


@router.callback_query(lambda callback: callback.data.startswith('dungeon_'))
async def get_boss_info(callback: CallbackQuery):
    boss_location = callback.data.split('_')[-1]
    boss_level = int(callback.data.split('_')[-2])

    matching_bosses = {}
    for boss_id, boss_info in bosses.items():
        if boss_info['level'] == boss_level and boss_info['location'] == boss_location:
            matching_bosses[boss_id] = boss_info['name']
    await callback.message.edit_text(
        text=f"Список возможных боссов для\n{FOREST_BTN[callback.data]}:\n\n",
        reply_markup=create_inline_kb(
            2, go_exit="forest_bosses", **matching_bosses))


@router.callback_query(lambda callback: callback.data.startswith('boss_'))
async def get_boss_info(callback: CallbackQuery):
    boss = callback.data
    boss_location = callback.data.split('_')[-1]
    boss_level = int(callback.data.split('_')[-2])
    log(callback, f"{bosses[boss]['name']}")
    await callback.message.edit_text(
        text=f"{bosses[boss]['text']}",
        reply_markup=create_inline_kb(
            1, go_exit=f"dungeon_{boss_level}_{boss_location}"))


@router.callback_query(Text(text='forest_bosses'))
@router.message(Command('bosses'))
async def process_start_command(callback_or_message: CallbackQuery | Message):
    user = callback_or_message.from_user.first_name
    users_db = load_log_file("database/users_db.json")
    if str(callback_or_message.from_user.id) in users_db:
        user = f"{users_db[str(callback_or_message.from_user.id)]['icon']}" \
               f"{users_db[str(callback_or_message.from_user.id)]['game_name']}"

    keyboard = create_inline_kb(2, 'dungeon_1_S', 'dungeon_1_N', 'dungeon_2_S', 'dungeon_2_N', 'dungeon_3_S',
                                'dungeon_3_N', 'dungeon_4_S', 'dungeon_4_N', 'dungeon_5_S', 'dungeon_5_N',
                                go_exit="start_forest",
                                )
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.message.edit_text(
            text=FOREST_LEXICON['choice_dungeon_location'].format(user),
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await callback_or_message.answer(
            text=FOREST_LEXICON['choice_dungeon_location'].format(user),
            parse_mode="HTML",
            reply_markup=keyboard)


@router.callback_query(lambda callback: callback.data.startswith('clan_'))
@router.message(Command('clan_p2w'))
async def process_get_statistic(callback_or_message: CallbackQuery | Message):
    if isinstance(callback_or_message, CallbackQuery):
        data_int = int(callback_or_message.data.split('_')[-1])
        clan_name = callback_or_message.data.split('_')[-2]
    else:
        data_int = 2
        clan_name = "[p2w] p2w"
    logs_list = get_logs_list(f"{clan_name}")
    users = load_log_file(f"logs_forest/{clan_name}/{logs_list[-1]}")

    if len(logs_list) == 1:
        data_int = 1
    elif len(logs_list) < data_int:
        await callback_or_message.message.edit_text(
            text=f"❌Данные по стае {clan_name} за выбранный период отсуствуют!"
                 f"\nОбновляйте данные каждый день и статистика будет корректной!",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=create_inline_kb(1, go_exit=f"clan_{clan_name}_2"))
        return

    users_old = load_log_file(f"logs_forest/{clan_name}/{logs_list[-data_int]}")
    all_users: dict = create_progress(users, users_old)
    ctime_last = datetime.fromtimestamp(getctime(f"logs_forest/{clan_name}/{logs_list[-1]}")).strftime('%d.%m (%H:%M)')
    ctime_data = datetime.fromtimestamp(getctime(f"logs_forest/{clan_name}/{logs_list[-data_int]}")).strftime(
        '%d.%m (%H:%M)')
    # Преобразуем строки обратно в объекты datetime
    datetime_last = datetime.strptime(ctime_last, '%d.%m (%H:%M)')
    datetime_data = datetime.strptime(ctime_data, '%d.%m (%H:%M)')

    # Вычисляем разницу во времени
    time_difference = datetime_last - datetime_data

    # Преобразуем разницу в часы
    hours_difference = int(time_difference.total_seconds() // 3600)
    log(callback_or_message, f"{clan_name} за {hours_difference} ч.")

    answer = FOREST_LEXICON['head_clans'].format(clan_name, ctime_last, len(users), len(users) - len(users_old))
    answer += f"⚜Прирост за период:\n{ctime_data} => {ctime_last} (~{hours_difference} ч.)\n\n"
    numb, all_exp_gain = 1, 0
    for key, value in sorted(all_users.items(), key=lambda x: -x[1]['exp_gain']):
        # icon = value['class'][0]
        answer += f"{numb}. <b>{value['name']}</b> >> <b>{value['exp']:,}</b> (+{value['exp_gain']:,}⚜)" \
                  f"\n".replace(",", ".")
        numb += 1
        all_exp_gain += value['exp_gain']
    answer += f"\n\n📈Общий прогресс за ~{hours_difference} ч. <b>+{all_exp_gain:,}</b>⚜\n⚙️Фильтр: по приросту"
    buttons: dict = {f"clan_{clan_name}_{data_int - 1 or 2}": "⬅️", f"clan_{clan_name}_{data_int + 1}": "➡️"}
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.message.edit_text(
            text=answer,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=create_inline_kb(2, go_exit="clan_statistic", **buttons))
    else:
        await callback_or_message.answer(
            text=answer,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=create_inline_kb(2, go_exit="clan_statistic", **buttons))


@router.callback_query(Text(text='forest_keys'))
@router.message(Command('keys'))
async def process_start_command(callback_or_message: CallbackQuery | Message):
    user = callback_or_message.from_user.first_name
    users_db = load_log_file("database/users_db.json")
    if str(callback_or_message.from_user.id) in users_db:
        user = f"{users_db[str(callback_or_message.from_user.id)]['icon']}" \
               f"{users_db[str(callback_or_message.from_user.id)]['game_name']}"
    buttons: dict = {
        "key_1_S": FOREST_BTN['key_1_S'], "key_1_N": FOREST_BTN['key_1_N'],
        "key_2_S": FOREST_BTN['key_2_S'], "key_2_N": FOREST_BTN['key_2_N'],
        "key_3_S": FOREST_BTN['key_3_S'], "key_3_N": FOREST_BTN['key_3_N'],
        "key_4_S": FOREST_BTN['key_4_S'], "key_4_N": FOREST_BTN['key_4_N'],
        "key_5_S": FOREST_BTN['key_5_S'], "key_5_N": FOREST_BTN['key_5_N'],
    }
    keyboard = create_inline_kb(
        2, go_exit="start_forest", **buttons
    )
    msg_params: dict = {
        "text": FOREST_LEXICON['choice_dungeon_key'].format(user),
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": keyboard
    }
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.message.edit_text(**msg_params)
    else:
        await callback_or_message.answer(**msg_params)


@router.callback_query(lambda callback: callback.data.startswith('key_'))
async def get_keys_info(callback: CallbackQuery):
    f_key = callback.data
    log(callback, forest_keys[f_key]['key_text'][:forest_keys[f_key]['key_text'].index('\n')])
    await callback.message.edit_text(
        text=f"{forest_keys[f_key]['key_text']}",
        reply_markup=create_inline_kb(
            1, go_exit=f"forest_keys"))


@router.callback_query(Text(text='forest_guide'))
async def process_start_command(callback: CallbackQuery):
    log(callback, f"Гайды")
    await callback.message.edit_text(
        text="⚙️Находится в разработке, загляните сюда позже⚙️",
        parse_mode="HTML",
        reply_markup=create_inline_kb(
            1, go_exit="start_forest",
        ))
