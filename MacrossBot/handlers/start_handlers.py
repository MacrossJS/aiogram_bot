import json
import os
import re
from datetime import datetime
from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.keyboard_builder import create_inline_kb

from lexicon.lexicon import *

router: Router = Router()
clan_info_regex = re.compile(r"^(?P<clan_tag>\[\w+] [\w-]+)",
                             re.IGNORECASE | re.MULTILINE)


def time_now() -> str:
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


def save_info(guild_tag: str, forest_users: dict) -> None:
    """Сохраним в json-файл"""
    folder_name = f"logs_forest/{guild_tag}"
    os.makedirs(folder_name, exist_ok=True)
    with open(
            f"{folder_name}/{guild_tag}_{datetime.today().strftime('%Y.%m.%d')}.json", 'w', encoding='utf-8'
    ) as save:
        json.dump(forest_users, save, ensure_ascii=False, indent=4)


@router.message(CommandStart())
async def process_start_command(message: Message):
    log(message, 'Запустил бота')
    qwew = message.from_user.id
    await message.answer(
        text=LEXICON['/start'].format(message.from_user.first_name),
        parse_mode="HTML",
        reply_markup=create_inline_kb(
            2, start_forest=MAIN_BTN['btn_start_forest'],
            start_tokyo=MAIN_BTN['btn_start_tokyo']))


@router.message(lambda message: message.forward_date is not None)
async def handle_forwarded_message(message: Message, bot: Bot):
    if message.forward_from.id != 6527978139:
        await message.answer(text='😎Принимается только пересланное сообщение из чата с ботом "Духи Леса"!')
        return
    if datetime.today().timestamp() - message.forward_date > 600:
        await message.answer(text='🕒Данное сообщение слишком старый, присылайте только актуальные данные!')
        return
    text = message.text
    match = clan_info_regex.search(text)
    if match:
        member_dict: dict = {}
        clan_tag = match.group('clan_tag')
        for user_name, exp, user_id in re.findall(r'(?P<name>\w+) \[.*] (?P<exp>\d+)⚜️ /p_(?P<user_id>\d+)', text):
            member_dict[user_id] = {'name': user_name, 'exp': int(exp)}
        # Создание папки и файла для записи данных
        log(message, f'прислал данные стаи {clan_tag}')
        save_info(clan_tag, member_dict)
        buttun = {f"clan_{clan_tag}_2": f"Перейти к статистике {clan_tag}"}
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await message.answer(text=f"✅Данные стаи {clan_tag} успешно сохранены.\n"
                                  f"⚙️Для удаления данных своей стаи из бота свяжитесь с разработчиком --> "
                                  f"<a href='tg://user?id=784724803'><b>Macross</b></a> / "
                                  f"<a href='tg://user?id=1660983940'><b>Baka-Baka</b></a>",
                             reply_markup=create_inline_kb(1, **buttun))
    else:
        await message.answer(f"Пересланное вами сообщение не содержит данных о стае!")
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@router.message(Command(commands='admins'))
async def process_admins_command(message: Message):
    log(message, '/admins')
    admin_ids = {784724803: {"title": "🧑‍💻Кодер", "name": "Macross"},
                 171429474: {"title": "✏️Редактор", "name": "Алина"},
                 5040538204: {"title": "🌚️ Мастер стаи p2w", "name": "13th "},
                 }
    answer = '⚙️Руководство:\n\n'
    for admin_id in admin_ids:
        answer += f'{admin_ids[admin_id]["title"]} >> <a href="tg://user?id={admin_id}">' \
                  f'<b>{admin_ids[admin_id]["name"]}</b></a>\n'
    await message.answer(text=answer, parse_mode="HTML")
