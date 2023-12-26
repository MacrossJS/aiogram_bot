from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery
from aiogram.types import Message
from rock_paper_scissors_bot.keyboards.keyboards import *
from rock_paper_scissors_bot.keyboards.keyboard_builder import create_inline_kb
from rock_paper_scissors_bot.lexicon.lexicon_ru import LEXICON_RU
from rock_paper_scissors_bot.services.services import get_bot_choice, get_winner

router: Router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'].format(message.from_user.first_name), reply_markup=yes_no_kb)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    new_kb = create_inline_kb(3, 'Menu',
                              go_exit='Назад',
                              btn_tel='Телефон',
                              btn_email='email',
                              btn_website='Web-сайт',
                              btn_vk='VK',
                              btn_tgbot='Наш телеграм-бот')
    await message.answer(text=LEXICON_RU['/help'], reply_markup=new_kb)


# Этот хэндлер срабатывает на согласие пользователя играть в игру
@router.message(Text(text=LEXICON_RU['yes_button']))
async def process_yes_answer(message: Message):
    await message.answer(text=LEXICON_RU['yes'], reply_markup=game_kb)


# Этот хэндлер срабатывает на отказ пользователя играть в игру
@router.message(Text(text=LEXICON_RU['no_button']))
async def process_no_answer(message: Message):
    await message.answer(text=LEXICON_RU['no'])


# Этот хэндлер срабатывает на любую из игровых кнопок
@router.message(Text(text=[LEXICON_RU['rock'],
                           LEXICON_RU['paper'],
                           LEXICON_RU['scissors']]))
async def process_game_button(message: Message):
    bot_choice = get_bot_choice()
    await message.answer(text=f'{LEXICON_RU["bot_choice"]} '
                              f'- {LEXICON_RU[bot_choice]}')
    winner = get_winner(message.text, bot_choice)
    await message.answer(text=LEXICON_RU[winner].format(message.from_user.first_name), reply_markup=yes_no_kb)


@router.message(Command(commands=['urls']))
async def process_post_urls(message: Message):
    await message.answer(
        text=LEXICON_RU['inline_buttons'].format(message.from_user.first_name),
        reply_markup=url_keyboard)


@router.message(Command(commands=['callback']))
async def process_callback_answer(message: Message):
    await message.answer(text=LEXICON_RU['callback_buttons'].format(message.from_user.first_name),
                         reply_markup=callback_keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'big_button_1_pressed'
@router.callback_query(Text(text=['big_button_1_pressed']))
async def process_button_1_press(callback: CallbackQuery):
    if callback.message.text != 'Была нажата БОЛЬШАЯ КНОПКА 1':
        await callback.message.edit_text(
            text='Была нажата БОЛЬШАЯ КНОПКА 1',
            reply_markup=callback.message.reply_markup)
    await callback.answer(text='Ура! Нажата кнопка 1', show_alert=True)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'big_button_2_pressed'
@router.callback_query(Text(text=['big_button_2_pressed']))
async def process_button_2_press(callback: CallbackQuery):
    await callback.message.edit_text(
        text='Была нажата БОЛЬШАЯ КНОПКА 2',
        reply_markup=callback.message.reply_markup)
