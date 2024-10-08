import asyncio
# import logging

from aiogram import Dispatcher
from aiogram.exceptions import TelegramNetworkError

from handlers import other_handlers, new_tokyo_handlers, forest_handlers, start_handlers
from keyboards.main_menu import set_main_menu
from aiogram import Bot
from config_data.config import Config, load_config

# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем логгер
# logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    try:
        # Конфигурируем логирование
        # logging.basicConfig(
        #     level=logging.INFO,
        #     format='%(filename)s:%(lineno)d #%(levelname)-8s '
        #            '[%(asctime)s] - %(name)s - %(message)s')

        # Выводим в консоль информацию о начале запуска бота
        # logger.info('Starting bot')
        # Инициализируем бот
        bot: Bot = Bot(token=config.tg_bot.token,
                       parse_mode='HTML')

        ADMINS = config.tg_bot.admin_ids

        dp: Dispatcher = Dispatcher()

        # Настраиваем главное меню бота
        await set_main_menu(bot)

        # Регистриуем роутеры в диспетчере
        dp.include_router(start_handlers.router)
        dp.include_router(forest_handlers.router)
        dp.include_router(new_tokyo_handlers.router)
        dp.include_router(other_handlers.router)

        # Пропускаем накопившиеся апдейты и запускаем polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except TelegramNetworkError as e:
        print(f"Ошибка сети Telegram: {e.message}")
    except Exception as e:
        if str(e) == "Telegram server says Request timeout error":
            print(f"Произошла ошибка: {str(e)}")


if __name__ == '__main__':
    asyncio.run(main())
