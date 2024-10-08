import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
import asyncpg
import asyncio

API_TOKEN = '6150056754:AAEWD7CG2qesUs5F0K1NBOYwh782lboU7Ww'
DATABASE_URL = 'postgresql://user:password@localhost:5432/database_name'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# Database setup
async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)


db_pool = asyncio.get_event_loop().run_until_complete(create_pool())


# Keyboards
def get_main_menu():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Создать заметку', callback_data='create_note'),
        InlineKeyboardButton('Все заметки', callback_data='view_notes')
    )


def get_back_button():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Назад', callback_data='main_menu')
    )


async def start(message: types.Message):
    await message.answer("Приветствую тебя в Лагере у тайного спуска!", reply_markup=get_main_menu())


@dp.callback_query_handler(Text(equals='main_menu'))
async def main_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Приветствую тебя в Лагере у тайного спуска!", reply_markup=get_main_menu())


@dp.callback_query_handler(Text(equals='create_note'))
async def create_note_start(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите название новой заметки:")
    dp.register_message_handler(get_note_title, state='waiting_for_title', user_id=callback_query.from_user.id)


async def get_note_title(message: types.Message):
    title = message.text
    await bot.send_message(message.from_user.id, "Введите текст заметки:")
    dp.register_message_handler(get_note_text, state='waiting_for_text', user_id=message.from_user.id, title=title)


async def get_note_text(message: types.Message, title):
    text = message.text
    user_id = message.from_user.id
    firstname = message.from_user.first_name
    username = message.from_user.username

    async with db_pool.acquire() as connection:
        await connection.execute('''
            INSERT INTO notes (user_id, firstname, username, title, text)
            VALUES ($1, $2, $3, $4, $5)
        ''', user_id, firstname, username, title, text)

    await message.answer("Заметка успешно создана!", reply_markup=get_main_menu())


@dp.callback_query_handler(Text(equals='view_notes'))
async def view_notes(callback_query: types.CallbackQuery):
    async with db_pool.acquire() as connection:
        notes = await connection.fetch('SELECT id, title FROM notes WHERE user_id=$1', callback_query.from_user.id)

    if notes:
        buttons = [InlineKeyboardButton(note['title'], callback_data=f"view_note_{note['id']}") for note in notes]
        markup = InlineKeyboardMarkup(row_width=1).add(*buttons).add(
            InlineKeyboardButton('Назад', callback_data='main_menu'))
        await bot.send_message(callback_query.from_user.id, "Ваши заметки:", reply_markup=markup)
    else:
        await bot.send_message(callback_query.from_user.id, "У вас нет заметок.", reply_markup=get_back_button())


@dp.callback_query_handler(Text(startswith='view_note_'))
async def view_note_detail(callback_query: types.CallbackQuery):
    note_id = int(callback_query.data.split('_')[-1])

    async with db_pool.acquire() as connection:
        note = await connection.fetchrow('SELECT * FROM notes WHERE id=$1', note_id)

    if note:
        text = f"{note['text']}\n\nАвтор: {note['firstname']} (@{note['username']})"
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton('Редактировать', callback_data=f"edit_note_{note['id']}"),
            InlineKeyboardButton('Удалить', callback_data=f"delete_note_{note['id']}"),
            InlineKeyboardButton('Назад', callback_data='view_notes')
        )
        await bot.send_message(callback_query.from_user.id, text, reply_markup=markup)


@dp.callback_query_handler(Text(startswith='edit_note_'))
async def edit_note_start(callback_query: types.CallbackQuery):
    note_id = int(callback_query.data.split('_')[-1])
    await bot.send_message(callback_query.from_user.id, "Введите новый текст заметки:")
    dp.register_message_handler(get_new_note_text, state='waiting_for_new_text', user_id=callback_query.from_user.id,
                                note_id=note_id)


async def get_new_note_text(message: types.Message, note_id):
    new_text = message.text

    async with db_pool.acquire() as connection:
        await connection.execute('''
            UPDATE notes
            SET text=$1
            WHERE id=$2
        ''', new_text, note_id)

    await message.answer("Заметка успешно обновлена!", reply_markup=get_main_menu())


@dp.callback_query_handler(Text(startswith='delete_note_'))
async def delete_note_start(callback_query: types.CallbackQuery):
    note_id = int(callback_query.data.split('_')[-1])
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Да', callback_data=f"confirm_delete_note_{note_id}"),
        InlineKeyboardButton('Нет', callback_data=f"view_note_{note_id}")
    )
    await bot.send_message(callback_query.from_user.id, "Вы уверены, что хотите удалить эту заметку?",
                           reply_markup=markup)


@dp.callback_query_handler(Text(startswith='confirm_delete_note_'))
async def delete_note_confirm(callback_query: types.CallbackQuery):
    note_id = int(callback_query.data.split('_')[-1])

    async with db_pool.acquire() as connection:
        await connection.execute('DELETE FROM notes WHERE id=$1', note_id)

    await callback_query.message.answer("Заметка успешно удалена!", reply_markup=get_main_menu())


if __name__ == '__main__':
    dp.register_message_handler(start, commands="start")
    executor.start_polling(dp, skip_updates=True)
