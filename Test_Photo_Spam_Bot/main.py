import asyncio
import logging
from sys import stdout

from aiogram import Dispatcher
from handlers import other_handlers, user_handlers
from keyboards.main_menu import set_main_menu
from aiogram import Bot
from config_data.config import Config, load_config

# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        stream=stdout,
        datefmt='%H:%M:%S',
        format='[{asctime}] {message}',
        style='{',
        level=logging.INFO
    )

    # Выводим в консоль информацию о начале запуска бота
    # logger.info('Starting bot')
    # Инициализируем бот
    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode='HTML')

    dp: Dispatcher = Dispatcher()

    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
