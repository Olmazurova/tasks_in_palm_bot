from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.models import Database
from keyboards.keyboard_utils import (main_keyboard, finish_keyboard,
                                      create_tasks_keyboard)
from lexicon.lexicon_ru import LEXICON_RU, LEXICON_BUTTONS_RU
from services.services import parsing_task, send_list_tasks
from states.states import FSMAddTask
from utils.utils import get_answer_of_tasks

router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(
        message: Message,
        state: FSMContext,
        db: Database,
        scheduler: AsyncIOScheduler
):
    """Обработчик команды /start."""
    # Проверяем есть ли пользователь в БД, если нет - заносим туда
    if db.select_user(message.from_user.id) is None:
        await db.insert_user(message.from_user)
    # Запускаем основной планировщик для пользователя
    scheduler.add_job(
        send_list_tasks,
        trigger='cron',
        hour=9,
        start_date=datetime.now(),
        id=f'{message.from_user.id} - main',
        kwargs={
            'bot': message.bot,
            'user_id': message.from_user.id,
            'db': db,
            'scheduler': scheduler,
        }
    )
    scheduler.start()

    await state.set_state(state=None)
    await message.answer(text=LEXICON_RU['/start'], reply_markup=main_keyboard)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message, state: FSMContext):
    """Обработчик команды /help."""
    await state.set_state(state=None)
    await message.answer(text=LEXICON_RU['/help'], reply_markup=main_keyboard)


# /add-task
@router.message(F.text == LEXICON_BUTTONS_RU['/add-task'])
async def process_btn_add_task(message: Message, state: FSMContext):
    """Обработчик команды /add-task."""
    await state.set_state(FSMAddTask.waiting_task)
    await message.answer(
        text=LEXICON_RU['/add-task'], reply_markup=finish_keyboard
    )


# /tasks-list
@router.message(F.text == LEXICON_BUTTONS_RU['/tasks-list'])
async def process_btn_tasks_list(
        message: Message, state: FSMContext, db: Database
):
    """Обработчик команды /tasks-list."""
    await state.set_state(state=None)
    tasks = await db.select_tasks(message.from_user.id)
    if not tasks:
        await message.answer(
            text=LEXICON_RU['no-tasks'], reply_markup=main_keyboard
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks)
        await message.answer(
            text=LEXICON_RU['/tasks-list'], reply_markup=tasks_keyboard
        )


# /finish-planning
@router.message(F.text == LEXICON_BUTTONS_RU['/finish-planning'])
async def process_btn_finish_task(message: Message, state: FSMContext):
    await state.set_state(state=None)
    await message.answer(
        text=LEXICON_RU['/finish-planning'], reply_markup=main_keyboard
    )


# done
@router.callback_query(F.data.in_(['done']))
async def process_done_task(
        callback: CallbackQuery, state: FSMContext, db: Database
):
    """Обработчик выполнения задачи."""
    await state.set_state(state=None)
    await db.update_task(
        callback.from_user.id, callback.data, field='done', value=1
    )
    await callback.answer(text=LEXICON_RU['done'])
    await get_answer_of_tasks(callback, db)


# rescheduling
@router.callback_query(F.data.in_(['rescheduling']))
async def process_rescheduling_task(callback: CallbackQuery, db: Database):
    """Обработчик переноса даты планирования задачи."""
    task = await db.get_task(callback.from_user.id, callback.data)
    await db.update_task(
        callback.from_user.id,
        callback.data,
        field='plan_date',
        value=task.plan_date + timedelta(days=1)
    )
    await callback.answer(text=LEXICON_RU['rescheduling'])
    await get_answer_of_tasks(callback, db)


# delete
@router.callback_query(F.data.in_(['del']))
async def process_delete_task(
        callback: CallbackQuery, state: FSMContext, db: Database
):
    """Обработчик удаления задачи из БД."""
    await state.set_state(state=None)
    await db.delete_task(callback.from_user.id, callback.data)
    await callback.answer(text=LEXICON_RU['delete'])
    await get_answer_of_tasks(callback, db)


# task
@router.message(F.text, StateFilter(FSMAddTask.waiting_task))
async def process_add_task(message: Message, db: Database):
    """Обработчик сообщения с задачами."""
    tasks = parsing_task(message)
    await db.insert_tasks(
        message.from_user.id,
        tasks,
        plan_date=message.date + timedelta(days=1)
    )
    await message.answer(text=LEXICON_RU['task'])


# Этот хендлер обрабатывает все остальные сообщения
@router.message()
async def send_answer(message: Message):
    await message.answer(text=LEXICON_RU['other_answer'])
