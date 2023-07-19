from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery
from aiogram.types import Message
from rock_paper_scissors_bot.keyboards.keyboards import *
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
    await message.answer(text=LEXICON_RU['/help'], reply_markup=yes_no_kb)


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
# с data 'big_button_1_pressed' или 'big_button_2_pressed'
@router.callback_query(Text(text=['big_button_1_pressed',
                                  'big_button_2_pressed']))
async def process_buttons_press(callback: CallbackQuery):
    await callback.answer()
