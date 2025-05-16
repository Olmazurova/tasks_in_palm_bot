from datetime import datetime, timedelta, date
from pprint import pprint

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram_i18n import I18nContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from lexicon.lexicon_ru import LEXICON_RU

router = Router()

@router.message(Command(commands='admin'))
async def process_admin_command(
    message: Message, scheduler: AsyncIOScheduler, i18n: I18nContext
):
    """Обработчик команды /admin."""
    pprint(scheduler.get_jobs())
    await message.answer(text=i18n.get('admin'))


@router.message(Command(commands='remove_jobs'))
async def process_remove_command(
    message: Message, scheduler: AsyncIOScheduler, i18n: I18nContext
):
    """Обработчик команды /admin."""
    scheduler.remove_all_jobs()
    await message.answer(text=i18n.get('remove_jobs'))
