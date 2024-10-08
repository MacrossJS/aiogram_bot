import os
from os.path import getctime
import json
from datetime import datetime

from aiogram import Router, Bot
from aiogram.filters import Text
from aiogram.types import CallbackQuery, InputMediaPhoto
from keyboards.keyboard_builder import create_inline_kb

from lexicon.lexicon import *
from lexicon.lexicon_tokyo import *
import locale

locale.setlocale(category=locale.LC_ALL, locale="ru_RU.utf8")

router: Router = Router()

referals = [387, 388, 411, 423, 503, 567, 573, 575, 586, 622, 735]


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
    log_list = os.listdir(f'logs_tokyo/')
    return sorted(log_list)


def load_log_file(log_file):
    """Загрузим инфо о последнем из json в словарь"""
    with open(log_file, 'r', encoding='utf-8') as last_file:
        logs = json.load(last_file)
    return logs


def load_achi_file(file_achi):
    """Загрузим инфо о достижениях из json в словарь"""
    with open(f"./{file_achi}", 'r', encoding='utf-8') as achi:
        achi_list = json.load(achi)
    return achi_list


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


@router.callback_query(Text(text='start_tokyo'))
async def process_start_command(callback: CallbackQuery):
    user = callback.from_user.first_name
    users_db = load_log_file("database/users_db.json")
    if str(callback.from_user.id) in users_db:
        user = f"{users_db[str(callback.from_user.id)]['icon']}{users_db[str(callback.from_user.id)]['game_name']}"
    await callback.message.edit_text(
        text=LEXICON['start_tokyo'].format(user),
        parse_mode="HTML",
        reply_markup=create_inline_kb(3, top_10=TOKYO_BTN['top_all'],
                                      progress=TOKYO_BTN['progress'],
                                      stats=TOKYO_BTN['stats'],
                                      reputation=TOKYO_BTN['reputation'],
                                      point_guardian=TOKYO_BTN['point_guardian'],
                                      noobs=TOKYO_BTN['noobs'],
                                      achievements_207=TOKYO_BTN['achievements'],
                                      dayly_tokyo=TOKYO_BTN['dayly'],
                                      maps_sewerage_1=TOKYO_BTN['maps']))


@router.callback_query(lambda callback: callback.data.startswith('top_'))
async def process_top_all(callback: CallbackQuery):
    top_count = callback.data.split('_')[1]
    logs_list = get_logs_list()
    log(callback.from_user, TOKYO_BTN[f'top_{top_count}'])
    users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
    users_old = load_log_file(f"logs_tokyo/{logs_list[-2]}")
    week_old = load_log_file(f"logs_tokyo/{logs_list[-7]}")
    old_7_users: dict = create_progress(users, week_old)
    users_db = load_log_file("database/users_db.json")
    ctime = datetime.fromtimestamp(getctime(f"logs_tokyo/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = LEXICON['head_tokyo'].format(ctime, len(users), len(users) - len(users_old))
    answer += f"🏆<b>Топ-{top_count} игроков Tokyo:</b>\n\n"
    numb = 1
    for key, value in sorted(users.items(), key=lambda x: -x[1]['exp']):
        icon = '✅' if int(key) in referals else ''
        afk = '💤' if old_7_users[key]['rise'] == 0 else ""
        if str(callback.from_user.id) in users_db and int(key) == users_db[str(callback.from_user.id)].get('tokyo_id'):
            afk = users_db[str(callback.from_user.id)]['icon']
        answer += f"{numb}. {afk}<a href='https://ntg.bz/user/#{key}'>{value['name']}</a>" \
                  f"[<b>{value['level']}</b>]{icon} >> {value['wins']:,}⚔ |  {value['exp']:,}⭐\n".replace(",", ".")
        numb += 1
        if numb > int(top_count):
            answer += "\n💤 - 7+ дней неактив!"
            break
    match top_count:
        case '10':
            reply_markup = create_inline_kb(3, go_exit="start_tokyo", X_top_10=TOKYO_BTN['X_top_10'],
                                            top_30=TOKYO_BTN['top_30'], top_50=TOKYO_BTN['top_50'])
        case '30':
            reply_markup = create_inline_kb(3, go_exit="start_tokyo", top_10=TOKYO_BTN['top_10'],
                                            X_top_30=TOKYO_BTN['X_top_30'], top_50=TOKYO_BTN['top_50'])
        case '50':
            reply_markup = create_inline_kb(3, go_exit="start_tokyo", top_10=TOKYO_BTN['top_10'],
                                            top_30=TOKYO_BTN['top_30'], X_top_50=TOKYO_BTN['X_top_50'])
        case _:
            reply_markup = create_inline_kb(3, go_exit="start_tokyo", top_10=TOKYO_BTN['top_10'],
                                            top_30=TOKYO_BTN['top_30'], top_50=TOKYO_BTN['top_50'])
    await callback.message.edit_text(text=answer, parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=reply_markup)


@router.callback_query(Text(text='progress'))
async def process_top_progress(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, TOKYO_BTN['progress'])
    users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
    users_old = load_log_file(f"logs_tokyo/{logs_list[-2]}")
    all_users: dict = create_progress(users, users_old)
    users_db = load_log_file("database/users_db.json")
    ctime = datetime.fromtimestamp(getctime(f"logs_tokyo/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = LEXICON['head_tokyo'].format(ctime, len(users), len(users) - len(users_old))
    answer += f"📈Прирост опыта за 12/18/24 часа:\n\n"
    numb = 1
    for key, value in sorted(all_users.items(), key=lambda x: -x[1]['rise']):
        if key in ("411", "4230", "3710") and callback.from_user.id != 1660983940:
            continue
        if value['rise'] <= 0:
            break
        ref = '✅' if int(key) in referals else ''
        person = ''
        if str(callback.from_user.id) in users_db and int(key) == users_db[str(callback.from_user.id)].get('tokyo_id'):
            person = users_db[str(callback.from_user.id)]['icon']
        answer += f"{numb}. {person}<a href='https://ntg.bz/user/#{key}'>{value['name']}</a>[<b>{value['level']}</b>]" \
                  f"{ref} >> +{value['rise']:,}⭐ |  +{value['kills']:,}⚔\n".replace(",", ".")
        numb += 1
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=create_inline_kb(3, top_10=TOKYO_BTN['top_all'],
                                                                   X_progress=TOKYO_BTN['X_progress'],
                                                                   stats=TOKYO_BTN['stats'],
                                                                   reputation=TOKYO_BTN['reputation'],
                                                                   point_guardian=TOKYO_BTN['point_guardian'],
                                                                   noobs=TOKYO_BTN['noobs'],
                                                                   achievements_207=TOKYO_BTN['achievements'],
                                                                   dayly_tokyo=TOKYO_BTN['dayly'],
                                                                   maps_sewerage_1=TOKYO_BTN['maps']))


@router.callback_query(lambda callback: callback.data.startswith('achievements_'))
async def process_top_achievements(callback: CallbackQuery):
    ach_id = callback.data.split('_')[1]
    story_line = ["207", "204", "209", "227", "226", "225", "234"]
    events = ["218", "219", "220", "221", "222"]
    winners = ["210", "211", "212", "223", "224"]
    if callback.message.photo:
        logs_list = get_logs_list()
        achi = load_achi_file("achievements.json")
        users_db = load_log_file("database/users_db.json")
        users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
        log(callback.from_user, achi[ach_id]["item_name"])

        answer = f'🎖Достижение: "<b>{achi[ach_id]["item_name"]}</b>"\n\n' \
                 f'<i>{achi[ach_id]["item_description"]}</i>\n\n'
        achs = []
        for uid, user_data in users.items():
            if (user_ach := user_data["achievements"]) and (ach := json.loads(user_ach).get(ach_id)):
                achs.append((uid, datetime.fromisoformat(ach)))
        for numb, (uid, ach) in enumerate(sorted(achs, key=lambda _: _[1]), 1):
            person = ''
            if str(callback.from_user.id) in users_db and int(uid) == \
                    users_db[str(callback.from_user.id)].get('tokyo_id'):
                person = users_db[str(callback.from_user.id)]['icon']
            answer += f"{numb}. {person}<a href='https://ntg.bz/user/#{uid}'>{users[uid]['name']}</a>" \
                      f"[<b>{users[uid]['level']}</b>] >> 🕐{ach.strftime('%d %B %Y в %H:%M')}\n"
            if numb == 13:
                break
        if not achs:
            answer += '1. Еще никем не получено...'
        if ach_id in story_line:
            keyboard = create_inline_kb(2, go_exit="menu_achievements",
                                        achievements_207=achi["207"]["item_name"],
                                        achievements_204=achi["204"]["item_name"],
                                        achievements_209=achi["209"]["item_name"],
                                        achievements_227=achi["227"]["item_name"],
                                        achievements_226=achi["226"]["item_name"],
                                        achievements_225=achi["225"]["item_name"],
                                        achievements_234=achi["234"]["item_name"])
        elif ach_id in events:
            keyboard = create_inline_kb(2, go_exit="menu_achievements",
                                        achievements_218=achi["218"]["item_name"],
                                        achievements_219=achi["219"]["item_name"],
                                        achievements_220=achi["220"]["item_name"],
                                        achievements_221=achi["221"]["item_name"],
                                        achievements_222=achi["222"]["item_name"])
        elif ach_id in winners:
            keyboard = create_inline_kb(2, go_exit="menu_achievements",
                                        achievements_210=achi["210"]["item_name"],
                                        achievements_211=achi["211"]["item_name"],
                                        achievements_212=achi["212"]["item_name"],
                                        achievements_223=achi["223"]["item_name"],
                                        achievements_224=achi["224"]["item_name"])
        else:
            keyboard = create_inline_kb(2, go_exit="menu_achievements",
                                        achievements_229=achi["229"]["item_name"],
                                        achievements_236=achi["236"]["item_name"],
                                        achievements_213=achi["213"]["item_name"],
                                        achievements_214=achi["214"]["item_name"],
                                        achievements_203=achi["203"]["item_name"],
                                        achievements_205=achi["205"]["item_name"],
                                        achievements_208=achi["208"]["item_name"])

        await callback.message.edit_media(media=InputMediaPhoto(media=achi[ach_id]["image"], caption=answer),
                                          parse_mode="HTML",
                                          disable_web_page_preview=True,
                                          reply_markup=keyboard)
    else:
        await edit_message_with_media(callback.message, 2)


@router.callback_query(Text(text='menu_achievements'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, "Меню ачивок")
    await callback.message.edit_media(
        media=InputMediaPhoto(media=TOKYO_MEDIA['NT_Logo'],
                              caption="Достижения жителей New Tokyo"),
        disable_web_page_preview=True,
        reply_markup=create_inline_kb(2, go_exit="go_exit",
                                      achievements_234=TOKYO_BTN['story_line'],
                                      achievements_222=TOKYO_BTN['events'],
                                      achievements_224=TOKYO_BTN['winners'],
                                      achievements_208=TOKYO_BTN['others']))


@router.callback_query(Text(text='stats'))
async def process_top_stats(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, TOKYO_BTN['stats'])
    users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
    users_old = load_log_file(f"logs_tokyo/{logs_list[-2]}")
    week_old = load_log_file(f"logs_tokyo/{logs_list[-7]}")
    old_7_users: dict = create_progress(users, week_old)
    users_db = load_log_file("database/users_db.json")
    ctime = datetime.fromtimestamp(getctime(f"logs_tokyo/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = LEXICON['head_tokyo'].format(ctime, len(users), len(users) - len(users_old))
    answer += "🧠Топ по сумме статов (💪-🤹‍♂-🧠-🕵️‍♂-❤)\n\n"
    numb = 1
    for key, value in sorted(users.items(), key=lambda x: -x[1]['sum_stats']):
        icon = '✅' if int(key) in referals else ''
        afk = '💤' if old_7_users[key]['rise'] == 0 else ""
        if str(callback.from_user.id) in users_db and int(key) == users_db[str(callback.from_user.id)].get('tokyo_id'):
            afk = users_db[str(callback.from_user.id)]['icon']
        answer += f"{numb}. {afk}<a href='https://ntg.bz/user/#{key}'>{value['name']}</a>[<b>{value['level']}</b>]" \
                  f"{icon} >> <b>{value['sum_stats']}</b> ({value['strength']}-{value['agility']}-{value['wisdom']}-" \
                  f"{value['intuition']}-{value['vitality']})\n"
        numb += 1
        if numb > 30:
            answer += "\n💤 - 7+ дней неактив!"
            break
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=create_inline_kb(3, top_10=TOKYO_BTN['top_all'],
                                                                   progress=TOKYO_BTN['progress'],
                                                                   X_stats=TOKYO_BTN['X_stats'],
                                                                   reputation=TOKYO_BTN['reputation'],
                                                                   point_guardian=TOKYO_BTN['point_guardian'],
                                                                   noobs=TOKYO_BTN['noobs'],
                                                                   achievements_207=TOKYO_BTN['achievements'],
                                                                   dayly_tokyo=TOKYO_BTN['dayly'],
                                                                   maps_sewerage_1=TOKYO_BTN['maps']))
    await callback.answer()


@router.callback_query(Text(text='reputation'))
async def process_top_reputation(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, TOKYO_BTN['reputation'])
    users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
    users_old = load_log_file(f"logs_tokyo/{logs_list[-2]}")
    week_old = load_log_file(f"logs_tokyo/{logs_list[-7]}")
    old_7_users: dict = create_progress(users, week_old)
    users_db = load_log_file("database/users_db.json")
    ctime = datetime.fromtimestamp(getctime(f"logs_tokyo/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = LEXICON['head_tokyo'].format(ctime, len(users), len(users) - len(users_old))
    answer += "🔔Топ по сумме репутаций (NT🟢 + Mars🔴 + Venera🟣)\n\n"
    numb = 1
    for key, value in sorted(users.items(), key=lambda x: -x[1]['sum_rep']):
        icon = '✅' if int(key) in referals else ''
        afk = '💤' if old_7_users[key]['rise'] == 0 else ""
        if str(callback.from_user.id) in users_db and int(key) == users_db[str(callback.from_user.id)].get('tokyo_id'):
            afk = users_db[str(callback.from_user.id)]['icon']
        answer += f"{numb}. {afk}<a href='https://ntg.bz/user/#{key}'>{value['name']}</a>[<b>{value['level']}</b>]" \
                  f"{icon} >> <b>{value['sum_rep']}</b> ({value['rep_NT']:,} + {value['rep_Mars']:,} + " \
                  f"{value['rep_Venera']:,})\n".replace(",", ".")
        numb += 1
        if numb > 50:
            answer += "\n💤 - 7+ дней неактив!"
            break
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=create_inline_kb(3, top_10=TOKYO_BTN['top_all'],
                                                                   progress=TOKYO_BTN['progress'],
                                                                   stats=TOKYO_BTN['stats'],
                                                                   X_reputation=TOKYO_BTN['X_reputation'],
                                                                   point_guardian=TOKYO_BTN['point_guardian'],
                                                                   noobs=TOKYO_BTN['noobs'],
                                                                   achievements_207=TOKYO_BTN['achievements'],
                                                                   dayly_tokyo=TOKYO_BTN['dayly'],
                                                                   maps_sewerage_1=TOKYO_BTN['maps']))


@router.callback_query(Text(text='point_guardian'))
async def process_point_guardian(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, TOKYO_BTN['point_guardian'])
    users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
    users_old = load_log_file(f"logs_tokyo/{logs_list[-2]}")
    week_old = load_log_file(f"logs_tokyo/{logs_list[-7]}")
    old_7_users: dict = create_progress(users, week_old)
    users_db = load_log_file("database/users_db.json")
    ctime = datetime.fromtimestamp(getctime(f"logs_tokyo/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = LEXICON['head_tokyo'].format(ctime, len(users), len(users) - len(users_old))
    answer += "🛡Топ по очкам наблюдателя\n\n"
    numb = 1
    for key, value in sorted(users.items(), key=lambda x: -x[1]['point_guardian']):
        icon = '✅' if int(key) in referals else ''
        afk = '💤' if old_7_users[key]['rise'] == 0 else ""
        if value['point_guardian'] == 0:
            answer += "\n💤 - 7+ дней неактив!"
            break
        if str(callback.from_user.id) in users_db and int(key) == users_db[str(callback.from_user.id)].get('tokyo_id'):
            afk = users_db[str(callback.from_user.id)]['icon']
        answer += f"{numb}. {afk}<a href='https://ntg.bz/user/#{key}'>{value['name']}</a>[<b>{value['level']}</b>]" \
                  f"{icon} >> 🛡<b>{value['point_guardian']}</b> | ☠<b>{value['defeat']}</b>\n".replace(",", ".")
        numb += 1
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=create_inline_kb(3, top_10=TOKYO_BTN['top_all'],
                                                                   progress=TOKYO_BTN['progress'],
                                                                   stats=TOKYO_BTN['stats'],
                                                                   reputation=TOKYO_BTN['reputation'],
                                                                   X_point_guardian=TOKYO_BTN['X_point_guardian'],
                                                                   noobs=TOKYO_BTN['noobs'],
                                                                   achievements_207=TOKYO_BTN['achievements'],
                                                                   dayly_tokyo=TOKYO_BTN['dayly'],
                                                                   maps_sewerage_1=TOKYO_BTN['maps']))


@router.callback_query(Text(text=['noobs', 'noobs_1']))
async def process_noobs_1(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, TOKYO_BTN['noobs'])
    users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
    users_old = load_log_file(f"logs_tokyo/{logs_list[-2]}")
    ctime = datetime.fromtimestamp(getctime(f"logs_tokyo/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = LEXICON['head_tokyo'].format(ctime, len(users), len(users) - len(users_old))
    answer += "👣Новые игроки за 12/24 часов:\n\n"
    numb = 1
    for key in sorted(set(users) - set(users_old), key=lambda x: -(users[x]['exp'])):
        answer += f"{numb}. <a href='https://ntg.bz/user/#{key}'>{users[key]['name']}</a>" \
                  f"[<b>{users[key]['level']}</b>] >> {users[key]['wins']:,}⚔ | {users[key]['exp']:,}⭐\n" \
                  f"".replace(",", ".")
        numb += 1
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=create_inline_kb(3, go_exit="start_tokyo",
                                                                   X_noobs_1=TOKYO_BTN['X_noobs_1'],
                                                                   noobs_7=TOKYO_BTN['noobs_7'],
                                                                   noobs_14=TOKYO_BTN['noobs_14']))


@router.callback_query(Text(text='noobs_7'))
async def process_noobs_7(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, TOKYO_BTN['noobs_7'])
    users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
    users_old = load_log_file(f"logs_tokyo/{logs_list[-7]}")
    ctime = datetime.fromtimestamp(getctime(f"logs_tokyo/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = LEXICON['head_tokyo'].format(ctime, len(users), len(users) - len(users_old))
    answer += f"👣Новые игроки за 7 дней\n\n"
    numb = 1
    for key in sorted(set(users) - set(users_old), key=lambda x: -(users[x]['exp'])):
        answer += f"{numb}. <a href='https://ntg.bz/user/#{key}'>{users[key]['name']}</a>" \
                  f"[<b>{users[key]['level']}</b>] >> {users[key]['wins']:,}⚔ | {users[key]['exp']:,}⭐\n" \
                  f"".replace(",", ".")
        numb += 1
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=create_inline_kb(3, go_exit="start_tokyo",
                                                                   noobs_1=TOKYO_BTN['noobs_1'],
                                                                   X_noobs_7=TOKYO_BTN['X_noobs_7'],
                                                                   noobs_14=TOKYO_BTN['noobs_14']))


@router.callback_query(Text(text='noobs_14'))
async def process_noobs_7(callback: CallbackQuery):
    logs_list = get_logs_list()
    log(callback.from_user, TOKYO_BTN['noobs_14'])
    users = load_log_file(f"logs_tokyo/{logs_list[-1]}")
    users_old = load_log_file(f"logs_tokyo/{logs_list[-14]}")
    ctime = datetime.fromtimestamp(getctime(f"logs_tokyo/{logs_list[-1]}")).strftime('%d.%m.%Y в %H:%M')
    answer = LEXICON['head_tokyo'].format(ctime, len(users), len(users) - len(users_old))
    answer += f"Новые игроки за 14 дней\n\n"
    numb = 1
    for key in sorted(set(users) - set(users_old), key=lambda x: -(users[x]['exp'])):
        answer += f"{numb}. <a href='https://ntg.bz/user/#{key}'>{users[key]['name']}</a>" \
                  f"[<b>{users[key]['level']}</b>] >> {users[key]['wins']:,}⚔ | {users[key]['exp']:,}⭐\n" \
                  f"".replace(",", ".")
        numb += 1
    await callback.message.edit_text(text=answer,
                                     parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=create_inline_kb(3, go_exit="start_tokyo",
                                                                   noobs_1=TOKYO_BTN['noobs_1'],
                                                                   noobs_7=TOKYO_BTN['noobs_7'],
                                                                   X_noobs_14=TOKYO_BTN['X_noobs_14']))


async def edit_message_with_media(message, way: int):
    if way == 1:
        await message.answer_photo(photo=TOKYO_MEDIA['dayly_tokyo'], caption="Ежедневные квесты Tokyo",
                                   reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                 X_dayly_tokyo=TOKYO_BTN['X_tokyo'],
                                                                 dayly_rim=TOKYO_BTN['dayly_rim'],
                                                                 dayly_with=TOKYO_BTN['dayly_with']))
    elif way == 2:
        await message.answer_photo(photo=TOKYO_MEDIA['NT_Logo'], caption="Достижения жителей New Tokyo",
                                   reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                 achievements_234=TOKYO_BTN['story_line'],
                                                                 achievements_222=TOKYO_BTN['events'],
                                                                 achievements_224=TOKYO_BTN['winners'],
                                                                 achievements_208=TOKYO_BTN['others']))
    else:
        await message.answer_photo(photo=TOKYO_MEDIA['photo_sewerage_1'], caption="Канализация 1 этаж",
                                   reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                 X_maps_sewerage_1=TOKYO_BTN['X_maps_sewerage_1'],
                                                                 maps_sewerage_2=TOKYO_BTN['maps_sewerage_2'],
                                                                 maps_old_park="🗺Старый парк",
                                                                 maps_druids_forest=TOKYO_BTN['maps_druids_forest'],
                                                                 maps_dark_lec=TOKYO_BTN['maps_dark_lec']))


@router.callback_query(Text(text='dayly_tokyo'))
async def callback_handler(callback: CallbackQuery):
    if callback.message.photo:
        log(callback.from_user, TOKYO_BTN['dayly_tokyo'])
        await callback.message.edit_media(
            media=InputMediaPhoto(media=TOKYO_MEDIA['dayly_tokyo'],
                                  caption='Ежедневные квесты Токио'),
            reply_markup=create_inline_kb(2, go_exit="go_exit",
                                          X_dayly_tokyo=TOKYO_BTN['X_tokyo'],
                                          dayly_rim=TOKYO_BTN['dayly_rim'],
                                          dayly_with=TOKYO_BTN['dayly_with']))
    else:
        log(callback.from_user, TOKYO_BTN['dayly'])
        await edit_message_with_media(callback.message, 1)


@router.callback_query(Text(text='dayly_rim'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, TOKYO_BTN['dayly_rim'])
    if callback.message.photo:
        await callback.message.edit_media(media=InputMediaPhoto(media=TOKYO_MEDIA['dayly_rim'],
                                                                caption='Ежедневные квесты Рим'),
                                          reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                        dayly_tokyo=TOKYO_BTN['dayly_tokyo'],
                                                                        X_dayly_rim=TOKYO_BTN['X_rim'],
                                                                        dayly_with=TOKYO_BTN['dayly_with']))


@router.callback_query(Text(text='dayly_with'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, TOKYO_BTN['dayly_with'])
    if callback.message.photo:
        await callback.message.edit_media(media=InputMediaPhoto(media=TOKYO_MEDIA['dayly_with'],
                                                                caption='Ежедневные квесты Молот ведьм'),
                                          reply_markup=create_inline_kb(2, go_exit="go_exit",
                                                                        dayly_tokyo=TOKYO_BTN['dayly_tokyo'],
                                                                        dayly_rim=TOKYO_BTN['dayly_rim'],
                                                                        X_with=TOKYO_BTN['X_with']))


@router.callback_query(Text(text='go_exit'))
async def callback_handler(callback: CallbackQuery, bot: Bot):
    try:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    except Exception as e:
        log(callback.from_user, e)
        await callback.answer("Не могу удалить сообщение, если ему более 48 часов!", show_alert=True)
    else:
        log(callback.from_user, 'Удалил собщение')
        await callback.answer("Вы успешно удалили сообщение!")


@router.callback_query(Text(text='maps_sewerage_1'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, TOKYO_BTN['maps_sewerage_1'])
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=TOKYO_MEDIA['photo_sewerage_1'], caption=TOKYO_BTN['maps_sewerage_1']),
            reply_markup=create_inline_kb(2, go_exit="go_exit", X_maps_sewerage_1=TOKYO_BTN['X_maps_sewerage_1'],
                                          maps_sewerage_2=TOKYO_BTN['maps_sewerage_2'], maps_old_park=TOKYO_BTN[
                    'maps_old_park'], maps_druids_forest=TOKYO_BTN['maps_druids_forest'],
                                          maps_dark_lec=TOKYO_BTN['maps_dark_lec']))
    else:
        await edit_message_with_media(callback.message, 0)
    await callback.answer()


@router.callback_query(Text(text='maps_sewerage_2'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, TOKYO_BTN['maps_sewerage_2'])
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=TOKYO_MEDIA['photo_sewerage_2'], caption=TOKYO_BTN['maps_sewerage_2']),
            reply_markup=create_inline_kb(2, go_exit="go_exit", maps_sewerage_1=TOKYO_BTN['maps_sewerage_1'],
                                          X_maps_sewerage_2=TOKYO_BTN['X_maps_sewerage_2'],
                                          maps_old_park=TOKYO_BTN['maps_old_park'],
                                          maps_druids_forest=TOKYO_BTN['maps_druids_forest'],
                                          maps_dark_lec=TOKYO_BTN['maps_dark_lec']))


@router.callback_query(Text(text='maps_old_park'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, TOKYO_BTN['maps_old_park'])
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=TOKYO_MEDIA['photo_old_park'], caption=TOKYO_BTN['maps_old_park']),
            reply_markup=create_inline_kb(2, go_exit="go_exit", maps_sewerage_1=TOKYO_BTN['maps_sewerage_1'],
                                          maps_sewerage_2=TOKYO_BTN['maps_sewerage_2'],
                                          X_maps_old_park=TOKYO_BTN['X_maps_old_park'],
                                          maps_druids_forest=TOKYO_BTN['maps_druids_forest'],
                                          maps_dark_lec=TOKYO_BTN['maps_dark_lec']))


@router.callback_query(Text(text='maps_druids_forest'))
async def callback_handler(callback: CallbackQuery):
    """druid forest map"""
    log(callback.from_user, TOKYO_BTN['maps_druids_forest'])
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=TOKYO_MEDIA['photo_druids_forest'],
                                  caption=TOKYO_BTN['maps_druids_forest']),
            reply_markup=create_inline_kb(2, go_exit="go_exit",
                                          maps_sewerage_1=TOKYO_BTN['maps_sewerage_1'],
                                          maps_sewerage_2=TOKYO_BTN['maps_sewerage_2'],
                                          maps_old_park=TOKYO_BTN['maps_old_park'],
                                          X_maps_druids_forest=TOKYO_BTN['X_maps_druids_forest'],
                                          maps_dark_lec=TOKYO_BTN['maps_dark_lec']))


@router.callback_query(Text(text='maps_dark_lec'))
async def callback_handler(callback: CallbackQuery):
    """Dark forest map"""
    log(callback.from_user, TOKYO_BTN['maps_dark_lec'])
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=TOKYO_MEDIA['photo_dark_lec'],
                                  caption=TOKYO_BTN['maps_dark_lec']),
            reply_markup=create_inline_kb(2, go_exit="go_exit",
                                          maps_sewerage_1=TOKYO_BTN['maps_sewerage_1'],
                                          maps_sewerage_2=TOKYO_BTN['maps_sewerage_2'],
                                          maps_old_park=TOKYO_BTN['maps_old_park'],
                                          maps_druids_forest=TOKYO_BTN['maps_druids_forest'],
                                          X_maps_dark_lec=TOKYO_BTN['X_maps_dark_lec']))


@router.callback_query(lambda callback: callback.data.startswith('X_'))
async def callback_handler(callback: CallbackQuery):
    log(callback.from_user, f"Вы уже нажимали кнопку {callback.data}!")
    await callback.answer("Вы уже просматриваете данную вкладку!\nПовторное нажатие не требуется!", show_alert=True)
