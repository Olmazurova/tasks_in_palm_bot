import logging
import time
from datetime import date, datetime, timedelta
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram_i18n import I18nContext, LazyProxy
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from database.models import Database
from keyboards.keyboard_utils import main_kb_builder, create_tasks_keyboard
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
        bot: Bot, 
        user_id, 
        db: Database, 
        scheduler: AsyncIOScheduler,
        i18n: I18nContext,
):
    """Отправляет пользователю список задач каждый день в 9 утра."""
    tasks = await db.select_tasks(user_id, plan_date=date.today())
    if not tasks:
        await bot.send_message(
            chat_id=user_id,
            text=i18n.get('no-tasks', case=0),
            reply_markup=main_kb_builder.as_markup(),
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, done=True)
        await bot.send_message(
            chat_id=user_id,
            text=i18n.get('check-tasks'),
            reply_markup=tasks_keyboard
        )
        job_date = date.today()
        scheduler.add_job(
            check_task_completion,
            trigger='interval',
            hours=3,
            start_date=datetime.now(),
            end_date=date.today() + timedelta(hours=21),
            id=f'{user_id} - {job_date}',
            kwargs={'user_id': user_id, 'i18n': i18n},
        )


async def check_task_completion(
        bot: Bot, 
        user_id: int, 
        db: Database, 
        scheduler: AsyncIOScheduler,
        i18n: I18nContext,
):
    """Спрашивает какие задачи выполнены и отправляет список задач."""
    tasks = await db.select_tasks(user_id, plan_date=date.today())
    job_date = date.today()

    if not tasks or datetime.now().hour > 21:
        print(f'{user_id} - {job_date}')
        scheduler.remove_job(id=f'{user_id} - {job_date}')
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, done=True)
        await bot.send_message(
            chat_id=user_id,
            text=i18n.get('check-tasks', date=job_date),
            reply_markup=tasks_keyboard
        )
