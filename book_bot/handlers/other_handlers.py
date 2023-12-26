import os

from aiogram import Router, F, Bot
from aiogram.types import Message


router: Router = Router()


# Типы содержимого тоже можно указывать по-разному.
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
