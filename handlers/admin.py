from datetime import datetime, timedelta, date

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from lexicon.lexicon_ru import LEXICON_RU

router = Router()

@router.message(Command(commands='admin'))
async def process_help_command(message: Message, scheduler: AsyncIOScheduler):
    """Обработчик команды /admin."""
    scheduler.print_jobs()
    await message.answer(text=LEXICON_RU['/admin'])
