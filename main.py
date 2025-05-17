import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_i18n import I18nContext, LazyProxy, I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from config_data.config import Config, load_config
from redis.asyncio import Redis
# Импортируем роутеры
from handlers import admin, user
from services import services
# Импортируем миддлвари
from middlewares.i18n import TranslatorMiddleware
# Импортируем вспомогательные функции для создания нужных объектов
from database.models import Database
from keyboards.set_menu import set_main_menu

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    redis = Redis(host='localhost')

    # Инициализируем объект хранилища
    storage = RedisStorage(redis=redis)

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    # Инициализируем другие объекты (пул соединений с БД, кеш и т.п.)
    database = Database(config.db.database)
    database.connection()

    # настройка перевода и локали
    # t_hub = TranslatorHub(
    #     {'ru': ('ru',)},
    #     translators=[
    #         FluentTranslator(
    #             locale='ru',
    #             translator=FluentBundle.from_string(
    #                 'ru',
    #                 'locales/ru/LC_MESSAGES',
    #                 use_isolating=False,
    #             )
    #         )
    #     ],
    #     root_locale='ru',
    # )
    i18n = FluentRuntimeCore(
        path='locales/{locale}/LC_MESSAGES',
        default_locale='ru',
    )
    i18n_middleware = I18nMiddleware(
        core=i18n,
        default_locale='ru',
    )
    i18n_middleware.setup(dispatcher=dp)

    # планировщик для отправки сообщений в определённое время
    job_stores = {
        'default': RedisJobStore()
    }
    scheduler = ContextSchedulerDecorator(
        AsyncIOScheduler(jobstores=job_stores))
    scheduler.ctx.add_instance(bot, Bot)
    scheduler.ctx.add_instance(database, Database)
    scheduler.ctx.add_instance(scheduler, AsyncIOScheduler)
    scheduler.ctx.add_instance(i18n, FluentRuntimeCore)
    scheduler.start()

    # Помещаем нужные объекты в workflow_data диспетчера
    dp.workflow_data.update(db=database, scheduler=scheduler)

    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Регистриуем роутеры
    logger.info('Подключаем роутеры')
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(services.router)

    # Регистрируем миддлвари
    logger.info('Подключаем миддлвари')
    # dp.update.middleware(TranslatorMiddleware())

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
