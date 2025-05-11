import logging
import time
from datetime import datetime
from aiogram import Router, Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.models import Database
from keyboards.keyboard_utils import main_keyboard, create_tasks_keyboard
from lexicon.lexicon_ru import LEXICON_SCHEDULED_MESSAGES_RU, LEXICON_RU

router = Router()


@router.shutdown()
async def on_shutdown(db: Database):
    """Закрывает соединение с БД."""
    logging.warning('Shutting down')
    db._conn.close()
    logging.warning("DB Connection closed")


def parsing_task(message: Message):
    """Разбирает сообщение на задачи."""
    tasks = message.text.split('\n')
    return tasks


async def send_list_tasks(
        bot: Bot, user_id, db: Database, scheduler: AsyncIOScheduler
):
    """Отправляет пользователю список задач каждый день в 9 утра."""
    tasks = db.select_tasks(user_id)
    if not tasks:
        await bot.send_message(
            chat_id=user_id,
            text=LEXICON_SCHEDULED_MESSAGES_RU['no-tasks'],
            reply_markup = main_keyboard,
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, done=True)
        await bot.send_message(
            chat_id=user_id,
            text=LEXICON_RU['/tasks-list'],
            reply_markup=tasks_keyboard
        )
        date = datetime.today()
        scheduler.add_job(
            check_task_completion,
            trigger='interval',
            hours=3,
            id=f'{user_id} - {date}',
            kwargs={
                'bot': bot,
                'user_id': user_id,
                'db': db,
                'scheduler': scheduler,
            },
        )


async def check_task_completion(
        bot: Bot, user_id: int, db: Database, scheduler: AsyncIOScheduler
):
    """Спрашивает какие задачи выполнены и отправляет список задач."""
    tasks = db.select_tasks(user_id)
    date = datetime.today()

    if not tasks or datetime.now().hour > 21:
        scheduler.shutdown(id=f'{user_id} - {date}')
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, done=True)
        await bot.send_message(
            chat_id=user_id,
            text=LEXICON_RU['check-tasks'],
            reply_markup=tasks_keyboard
        )
