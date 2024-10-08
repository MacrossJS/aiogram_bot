import os

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, InputMediaPhoto

from lexicon.lexicon import *

router: Router = Router()


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


# Этот хэндлер будет реагировать на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@router.message()
async def send_echo(message: Message):
    await message.answer(f'{message.from_user.first_name}, бот не знает команду "{message.text}"')
