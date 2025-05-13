from datetime import datetime, timedelta, date

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.models import Database
from filters.filters import IsDelTaskCallbackData
from keyboards.keyboard_utils import (main_kb_builder, finish_kb_builder)
from lexicon.lexicon_ru import LEXICON_RU
from services.services import parsing_task, send_list_tasks
from states.states import FSMTask
from utils.utils import (get_callback_answer_of_tasks,
                         get_message_answer_of_tasks)

router = Router()


@router.message(CommandStart())
async def process_start_command(
        message: Message,
        state: FSMContext,
        db: Database,
        scheduler: AsyncIOScheduler
):
    """Обработчик команды /start."""
    # Проверяем есть ли пользователь в БД, если нет - заносим туда
    user = await db.select_user(message.from_user.id)
    if not user:
        await db.insert_user(message.from_user)
    # Запускаем основной планировщик для пользователя
    scheduler.add_job(
        send_list_tasks,
        trigger='cron',
        hour=20,
        minute=0,
        start_date=datetime.now(),
        id=f'main: user {message.from_user.id}, date {message.date}',
        kwargs={
            'bot': message.bot,
            'user_id': message.from_user.id,
            'db': db,
            'scheduler': scheduler,
        }
    )
    scheduler.start()

    await state.set_state(state=FSMTask.start)
    await message.answer(
        text=LEXICON_RU['/start'], reply_markup=main_kb_builder.as_markup()
    )


@router.message(Command(commands='help'))
async def process_help_command(message: Message, state: FSMContext):
    """Обработчик команды /help."""
    await state.set_state(state=FSMTask.help)
    await message.answer(
        text=LEXICON_RU['/help'], reply_markup=main_kb_builder.as_markup()
    )


@router.message(Command(commands='add_task'))
@router.callback_query(F.data.in_(['/add_task']))
async def process_btn_add_task(
        update: CallbackQuery | Message, state: FSMContext
):
    """Обработчик команды /add_task."""
    await state.set_state(FSMTask.waiting_task)
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(
            text=LEXICON_RU['/add_task'],
            reply_markup=finish_kb_builder.as_markup(),
        )
    else:
        await update.answer(
            text=LEXICON_RU['/add_task'],
            reply_markup=finish_kb_builder.as_markup(),
        )


@router.message(Command(commands='tasks_list'))
@router.callback_query(F.data.in_(['/tasks_list']))
async def process_btn_tasks_list(
        update: CallbackQuery | Message, state: FSMContext, db: Database
):
    """Обработчик команды /tasks_list или нажатия на кнопку."""
    if isinstance(update, CallbackQuery):
        await get_callback_answer_of_tasks(update, db)
    else:
        await state.set_state(state=FSMTask.task_list)
        await get_message_answer_of_tasks(update, db)


@router.message(
    Command(commands='finish_planning'), StateFilter(FSMTask.waiting_task)
)
@router.callback_query(
    F.data.in_(['/finish_planning']), StateFilter(FSMTask.waiting_task)
)
async def process_btn_finish_task(
        update: CallbackQuery | Message,
        state: FSMContext,
):
    """Обработчик нажатия кнопки "Завершить планирование"."""
    await state.set_state(state=None)
    if isinstance(update, CallbackQuery):
        await update.message.answer(
            text=LEXICON_RU['/finish_planning'],
            reply_markup=main_kb_builder.as_markup(),
        )
    else:
        await update.answer(
            text=LEXICON_RU['/finish_planning'],
            reply_markup=main_kb_builder.as_markup(),
        )


@router.callback_query(F.data.in_(['back']))
async def process_btn_back(
        callback: CallbackQuery, state: FSMContext,
):
    """Обработчик нажатия кнопки "Назад"."""
    if await state.get_state() == FSMTask.start:
        await callback.message.edit_text(
            text=LEXICON_RU['/start'], reply_markup=main_kb_builder.as_markup()
        )
    elif await state.get_state() == FSMTask.help:
        await callback.message.edit_text(
            text=LEXICON_RU['/help'], reply_markup=main_kb_builder.as_markup()
        )
    else:
        await callback.message.edit_text(
            text=LEXICON_RU['/add_task'],
            reply_markup=main_kb_builder.as_markup(),
        )


@router.callback_query(F.data.in_(['done']))
async def process_done_task(
        callback: CallbackQuery, db: Database
):
    """Обработчик выполнения задачи."""
    await db.update_task(
        callback.from_user.id, callback.data, field='done', value=1
    )
    await callback.answer(text=LEXICON_RU['done'])
    await get_callback_answer_of_tasks(callback, db)


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
    await get_callback_answer_of_tasks(callback, db)


@router.callback_query(IsDelTaskCallbackData())
async def process_delete_task(
        callback: CallbackQuery, db: Database
):
    """Обработчик удаления задачи из БД."""
    await db.delete_task(callback.from_user.id, callback.data.split()[0])
    await callback.answer(text=LEXICON_RU['delete'])
    await get_callback_answer_of_tasks(callback, db)


@router.message(F.text, StateFilter(FSMTask.waiting_task))
async def process_add_task(message: Message, db: Database):
    """Обработчик сообщения с задачами."""
    tasks = parsing_task(message)
    plan_date = date.today() + timedelta(days=1)

    await db.insert_tasks(
        message.from_user.id,
        tasks,
        plan_date=plan_date
    )
    await message.answer(text=LEXICON_RU['task'])


@router.message()
async def send_answer(message: Message):
    """Обработчик всех остальных сообщений."""
    await message.answer(text=LEXICON_RU['other_answer'])
