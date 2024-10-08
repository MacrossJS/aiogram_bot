import json
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from filters.fsm import FSMFillForm
from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart, Text, StateFilter
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from keyboards.keyboard_builder import create_inline_kb

from lexicon.lexicon import *
import locale

locale.setlocale(category=locale.LC_ALL, locale="ru_RU.utf8")

router: Router = Router()

all_notes = {}


def time_now():
    """Получим текущее время с учетом ОС"""
    return datetime.today().strftime('%H:%M:%S')


def log(user, log_text):
    """Сформируем вывод красивого лога
    цвет + текущее время + имя бота"""
    color = 90 + user.id % 10
    user_info = f"{user.first_name} {user.last_name if user.last_name else ''} | @{user.username} ({user.id})"
    print(f"\033[{color}m{time_now()}: [{user_info}] --> {log_text}")


def save_info():
    """Сохраним заметки в json-файл"""
    with open(f"database/notes.json", 'w', encoding='utf-8') as save:
        json.dump(all_notes, save, indent=4, ensure_ascii=False)


def load_notes():
    """Загрузим инфо о заметках из json в словарь"""
    with open(f"database/notes.json", 'r', encoding='utf-8') as notes:
        notes_list = json.load(notes)
    print(notes_list)
    return notes_list


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    user = message.from_user
    log(user, 'Запустил бота')
    await message.answer(
        text=LEXICON['/start'].format(message.from_user.first_name),
        parse_mode="HTML",
        reply_markup=create_inline_kb(2, create_note=LEXICON_BTN['create'],
                                      all_notes=LEXICON_BTN['all_notes']))


@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='Отменять нечего.')


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы отменили операцию')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


@router.message(Command(commands='create'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    user = message.from_user
    log(user, 'Вводит название')
    await message.answer(text='Пожалуйста, введите название заметки')
    # Устанавливаем состояние ожидания ввода названия
    await state.set_state(FSMFillForm.fill_note_name)


@router.message(StateFilter(FSMFillForm.fill_note_name), F.text, lambda x: 1 <= len(x.text) <= 20)
async def process_name_sent(message: Message, state: FSMContext):
    # Сохраняем введенное имя в хранилище по ключу "name"
    user = message.from_user
    log(user, f'Название: {message.text}')
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите полный текст заметки или /cancel для отмены.')
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_note_text)


@router.message(StateFilter(FSMFillForm.fill_note_name))
async def warning_not_name(message: Message):
    await message.answer(text='Имя заметки не долго превышать 20 символов!\n\n'
                              'Если вы хотите прервать создание заметки - '
                              'отправьте команду /cancel')


@router.message(StateFilter(FSMFillForm.fill_note_text), F.text)
async def process_wish_news_press(message: Message, state: FSMContext):
    user = message.from_user
    log(user, f'Текст: {message.text}')
    # Сохраняем данные о получении новостей по ключу "wish_news"
    await state.update_data(text=message.text)
    # Добавляем в "базу данных" анкету пользователя
    user_dict = await state.get_data()
    all_notes[user_dict['name']] = user_dict['text']
    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение о выходе из машины состояний
    save_info()
    await message.answer(text='Ваша заметка успешно создана')


@router.message(Command(commands='notes'))
async def process_admins_command(message: Message):
    answer = ''
    for note in all_notes:
        answer += f'📝 {note}\n'
    await message.answer(
        text=answer,
        parse_mode="HTML",
        reply_markup=create_inline_kb(2, update_note=LEXICON_BTN['update_note'],
                                      delete_note=LEXICON_BTN['delete_note']))


@router.message(Command(commands='admins'))
async def process_admins_command(message: Message):
    admin_ids = {
        171429474: "🫦Алина - Архимать",
        784724803: '🤖Macross - кодер',
    }
    answer = ''
    for aid in admin_ids:
        answer += f'<a href="tg://user?id={aid}">{admin_ids[aid]}</a>\n'
    await message.answer(text=answer, parse_mode="HTML")


