import os
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message, ChatMemberUpdated, ChatMember
from aiogram.filters import Command, CommandStart, Text, ChatMemberUpdatedFilter
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from keyboards.keyboard_builder import create_reply_kb

from lexicon.lexicon import *

router: Router = Router()


def time_now():
    """Получим текущее время с учетом ОС"""
    return datetime.today().strftime('%H:%M:%S')


def log(user, log_text):
    """Сформируем вывод красивого лога
    цвет + текущее время + имя бота"""
    color = 90 + user.id % 10
    user_info = f"{user.first_name} {user.last_name if user.last_name else ''} | @{user.username} ({user.id})"
    print(f"\033[{color}m{time_now()}: [{user_info}] --> {log_text}")


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON['/help'], reply_markup=create_reply_kb())


@router.message(F.content_type.in_({'photo', 'audio', 'voice', 'video', 'document'}))
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


@router.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    user = message.from_user
    photo = message.photo[-1]
    save_folder = f"{user.id}_@{user.username}"
    if not os.path.exists(f"tmp/{save_folder}"):
        os.mkdir(f"tmp/{save_folder}")
    file_name = f"{message.date.strftime('%Y.%m.%d_в_%H-%M-%S')}_{photo.file_unique_id}_" \
                f"{photo.width}x{photo.height}.jpg"
    print(file_name)
    await bot.download(message.photo[-1], destination=f"tmp/{save_folder}/{file_name}")
    await message.answer(f'Изображение {file_name} сохранено успешно!')


@router.message(F.location)
async def handle_location(message: Message):
    if message.location:
        user = message.from_user
        log(user, 'Запустил бота')
        latitude = message.location.latitude
        longitude = message.location.longitude
        log(user, f"Координаты: {latitude}, {longitude}")
        await message.reply(f"{message.from_user.first_name}, Ваши координаты: {latitude}, {longitude}")


@router.chat_member(ChatMemberUpdatedFilter(chat_member_updated=True))
async def greet_new_member(message: Message, event: ChatMemberUpdated):
    new_member = event.new_chat_member.user
    chat_id = event.chat.id

    if new_member:
        await message.answer(f"Добро пожаловать, {new_member.first_name}!")
