import logging
from datetime import date, datetime, timedelta

from aiogram import Bot, Router
from aiogram.types import Message
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.models import Database
from keyboards.keyboard_utils import create_tasks_keyboard, main_kb_builder
from utils.constants import HOUR_FINISH, HOURS_INTERVAL

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
        user_id: int,
        db: Database, 
        scheduler: AsyncIOScheduler,
        i18n: FluentRuntimeCore,
):
    """Отправляет пользователю список задач каждый день в 9 утра."""
    job_date = date.today()
    tasks = await db.select_tasks(user_id, plan_date=job_date)
    if not tasks:
        await bot.send_message(
            chat_id=user_id,
            text=i18n.get('no-tasks', case=0),
            reply_markup=main_kb_builder.as_markup(),
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, i18n, done=True)
        await bot.send_message(
            chat_id=user_id,
            text=i18n.get('check-tasks', date=job_date),
            reply_markup=tasks_keyboard
        )

        scheduler.add_job(
            check_task_completion,
            trigger='interval',
            hours=HOURS_INTERVAL,
            start_date=datetime.now(),
            end_date=date.today() + timedelta(hours=HOUR_FINISH),
            id=f'{user_id} - {job_date}',
            kwargs={'user_id': user_id},
        )


async def check_task_completion(
        bot: Bot, 
        user_id: int, 
        db: Database, 
        scheduler: AsyncIOScheduler,
        i18n: FluentRuntimeCore,
):
    """Спрашивает какие задачи выполнены и отправляет список задач."""
    job_date = date.today()
    tasks = await db.select_tasks(user_id, plan_date=job_date)

    if not tasks or datetime.now().hour > 21:
        scheduler.remove_job(id=f'{user_id} - {job_date}')
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, i18n=i18n, done=True)
        await bot.send_message(
            chat_id=user_id,
            text=i18n.get('check-tasks', date=job_date),
            reply_markup=tasks_keyboard
        )
