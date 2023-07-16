from aiogram import Bot
from aiogram.types import BotCommand

from rock_paper_scissors_bot.lexicon.lexicon_ru import LEXICON_COMMANDS_RU
import logging

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command, description in LEXICON_COMMANDS_RU.items()]
    logger.info(main_menu_commands)
    await bot.set_my_commands(main_menu_commands)
