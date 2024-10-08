from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from keyboards.keyboard_builder import create_inline_kb

from lexicon.lexicon import *

router: Router = Router()

COUNTER = 0


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer_photo(photo=LEXICON_MEDIA['btn_1'], caption="Первое сообщение",
                               reply_markup=create_inline_kb(3, "btn_1", "btn_2", "btn_3", "btn_4", "btn_5", "btn_6"))


@router.callback_query(lambda callback: callback.data.startswith('btn_'))
async def callback_handler(callback: CallbackQuery):
    global COUNTER
    COUNTER += 1
    await callback.message.edit_media(
        media=InputMediaPhoto(media=LEXICON_MEDIA[f'{callback.data}'], caption=f'Изменили картинку {COUNTER} раз'),
        reply_markup=create_inline_kb(3, "btn_1", "btn_2", "btn_3", "btn_4", "btn_5", "btn_6"))
