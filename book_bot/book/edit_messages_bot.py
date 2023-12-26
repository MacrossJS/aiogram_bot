from pprint import pprint

from aiogram import Bot, Dispatcher, F
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, InputMediaAudio,
                           InputMediaDocument, InputMediaPhoto,
                           InputMediaVideo, Message, InputFile)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart, Text, Command
from aiogram.exceptions import TelegramBadRequest
from environs import Env

# Достанем инфу из окружения или файла .env
env = Env()
env.read_env()

BOT_TOKEN = env('TG_TOKEN', parse_mode='HTML')

bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher()

LEXICON: dict[str, str] = {
    'audio': '🎶 Аудио',
    'text': '📃 Текст',
    'photo': '🖼 Фото',
    'video': '🎬 Видео',
    'document': '📑 Документ',
    'voice': '📢 Голосовое сообщение',
    'text_1': 'Это обыкновенное текстовое сообщение, его можно легко отредактировать другим текстовым сообщением, но нельзя отредактировать сообщением с медиа.',
    'text_2': 'Это тоже обыкновенное текстовое сообщение, которое можно заменить на другое текстовое сообщение через редактирование.',
    'photo_id1': 'AgACAgIAAxkBAAINl2TEevUIi4HsAX4R_FBcrRafgQHwAAIZ0TEbeoIgStzwYeZXRP-xAQADAgADbQADLwQ',
    'photo_id2': 'AgACAgIAAxkBAAINmWTEeyQ3GuboSVnKZ5PAanY4kCdPAAIa0TEbeoIgSpO41A-s2VveAQADAgADeAADLwQ',
    'voice_id1': 'AwACAgIAAxkBAAINm2TEe3ij2lEHy3B0scaPlKfTaBikAALVNwACeoIgSuJVoYSUb2KrLwQ',
    'voice_id2': 'CQACAgIAAxkBAAIQT2WJy1AZ-CQ1Oo7fdZb8hFnwxpFHAALtRAACYydRSM7xUjk7aRKZMwQ',
    'audio_id1': 'CQACAgIAAxkBAAIN-WTEwHoPPgcaLReYRYaO_JO-qqxSAAJWNQACkKMgSlqbKCXVE3MiLwQ',
    'audio_id2': 'CQACAgIAAxkBAAIN-2TEwJ7OFWOQQ2dbsJ3yGbezGFwEAAJXNQACkKMgSuewIRQ2qISSLwQ',
    'document_id1': 'BQACAgIAAxkBAAINo2TEfGWUTsXmBLQakrpZBfnqnQKnAALZNwACeoIgSiPzjlcg3b-RLwQ',
    'document_id2': 'BQACAgIAAxkBAAINpWTEfIuZf9ke7TNaUk7VYUDE7k05AALaNwACeoIgSmqHH_oY-_ROLwQ',
    'video_id1': 'BAACAgIAAxkBAAINp2TEfLyJATjgtUCC8zuGLWS-jDnIAALbNwACeoIgSqwWV9zj4saYLwQ',
    'video_id2': 'BAACAgIAAxkBAAINqWTEfOAbqxrYDmr4riF7maC9GFWQAALeNwACeoIgSr9QwCj6d6_1LwQ',
}


# Функция для генерации клавиатур с инлайн-кнопками
def get_markup(width: int, *args, **kwargs) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []
    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON[button] if button in LEXICON else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    markup = get_markup(2, 'video')
    await message.answer_photo(
        photo=LEXICON['photo_id1'],
        caption='Это фото 1',
        reply_markup=markup)


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
@dp.callback_query(Text(text=['text', 'audio', 'video', 'document', 'photo', 'voice']))
async def process_button_press(callback: CallbackQuery):
    # print(callback.message.json(indent=4, exclude_none=True))
    if callback.message.photo:
        markup = get_markup(1, 'document')
        await callback.message.edit_media(
            media=InputMediaVideo(media=LEXICON['video_id1'],
                                  caption='Это видео 1'), reply_markup=markup)
    if callback.message.video:
        markup = get_markup(1, 'audio')
        await callback.message.edit_media(
            media=InputMediaDocument(media=LEXICON['document_id2'],
                                     caption='Это документ 2'), reply_markup=markup)
    if callback.message.document:
        markup = get_markup(1, 'photo')
        await callback.message.edit_media(
            media=InputMediaAudio(media=LEXICON['audio_id1'],
                                  caption='Это музыка'), reply_markup=markup)

    if callback.message.audio:
        markup = get_markup(1, 'video')
        await callback.message.edit_media(
            media=InputMediaPhoto(media=LEXICON['photo_id2'],
                                  caption='Это фото 2'), reply_markup=markup)


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    with open("voice_1.ogg", 'rb') as voice_file:
        voice = InputFile(voice_file)
        await bot.send_voice(message.chat.id, voice)


@dp.message(F.content_type.in_({'photo', 'audio', 'voice', 'video', 'document'}))
async def send_echo(message: Message):
    print(message.json(indent=4, exclude_none=True))
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


# Этот хэндлер будет срабатывать на все остальные сообщения
@dp.message()
async def send_echo(message: Message):
    print(message.json(indent=4, exclude_none=True))
    await message.answer(
        text='Не понимаю')


if __name__ == '__main__':
    dp.run_polling(bot)
