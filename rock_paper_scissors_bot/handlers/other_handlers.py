from aiogram import Router
from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message
from rock_paper_scissors_bot.lexicon.lexicon_ru import LEXICON_RU

router: Router = Router()


# Этот хэндлер будет срабатывать на команду "/delmenu"
@router.message(Command(commands='delmenu'))
async def del_main_menu(message: Message, bot: Bot):
    await bot.delete_my_commands()
    await message.answer(text='Кнопка "Menu" удалена')


# Хэндлер для сообщений, которые не попали в другие хэндлеры
@router.message()
async def send_answer(message: Message):
    await message.answer(text=LEXICON_RU['other_answer'])
