from datetime import datetime, timedelta, date

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext, LazyProxy
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.models import Database
from keyboards.keyboard_utils import (main_kb_builder, finish_kb_builder,
                                      DoneCallbackFactory, DelCallbackFactory,
                                      TransferCallbackFactory)
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
        scheduler: AsyncIOScheduler,
        i18n: I18nContext,
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
        hour=9,
        # minute=20,
        start_date=datetime.now(),
        id=f'main: user {message.from_user.id}, date {message.date}',
        kwargs={'user_id': message.from_user.id}
    )
    await state.set_state(state=FSMTask.start)
    await message.answer(
        text=i18n.get('start'), reply_markup=main_kb_builder.as_markup()
    )


@router.message(Command(commands='help'))
async def process_help_command(
    message: Message, state: FSMContext, i18n: I18nContext
):
    """Обработчик команды /help."""
    await state.set_state(state=FSMTask.help)
    await message.answer(
        text=i18n.get('help'), reply_markup=main_kb_builder.as_markup()
    )


@router.message(Command(commands='add_task'))
@router.callback_query(F.data.in_([LazyProxy('cmd_add_task')]))
async def process_btn_add_task(
        update: CallbackQuery | Message, state: FSMContext,  i18n: I18nContext
):
    """Обработчик команды /add_task."""
    await state.set_state(FSMTask.waiting_task)
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(
            text=i18n.get('add_task'),
            reply_markup=finish_kb_builder.as_markup(),
        )
    else:
        await update.answer(
            text=i18n.get('add_task'),
            reply_markup=finish_kb_builder.as_markup(),
        )


@router.message(Command(commands='tasks_list'))
@router.callback_query(F.data.in_([LazyProxy('cmd_tasks_list')]))
async def process_btn_tasks_list(
        update: CallbackQuery | Message, 
        state: FSMContext, 
        db: Database,
        i18n: I18nContext,
):
    """Обработчик команды /tasks_list или нажатия на кнопку."""
    if isinstance(update, CallbackQuery):
        await get_callback_answer_of_tasks(update, db, i18n)
    else:
        await state.set_state(state=FSMTask.task_list)
        await get_message_answer_of_tasks(update, db, i18n)


@router.message(
    Command(commands='finish_planning'), StateFilter(FSMTask.waiting_task)
)
@router.callback_query(
    F.data.in_([LazyProxy('cmd_finish_planning')]), 
    StateFilter(FSMTask.waiting_task),
)
async def process_btn_finish_task(
        update: CallbackQuery | Message,
        state: FSMContext,
        i18n: I18nContext,
):
    """Обработчик нажатия кнопки "Завершить планирование"."""
    await state.set_state(state=None)
    if isinstance(update, CallbackQuery):
        await update.message.answer(
            text=i18n.get('finish_planning'),
            reply_markup=main_kb_builder.as_markup(),
        )
    else:
        await update.answer(
            text=i18n.get('finish_planning'),
            reply_markup=main_kb_builder.as_markup(),
        )


@router.callback_query(F.data.in_(['back']))
async def process_btn_back(
        callback: CallbackQuery, state: FSMContext,  i18n: I18nContext,
):
    """Обработчик нажатия кнопки "Назад"."""
    if await state.get_state() == FSMTask.start:
        await callback.message.edit_text(
            text=i18n.get('start'), reply_markup=main_kb_builder.as_markup()
        )
    elif await state.get_state() == FSMTask.help:
        await callback.message.edit_text(
            text=i18n.get('help'), reply_markup=main_kb_builder.as_markup()
        )
    else:
        await callback.message.edit_text(
            text=i18n.get('add_task'),
            reply_markup=main_kb_builder.as_markup(),
        )


@router.callback_query(DoneCallbackFactory.filter())
async def process_done_task(
        callback: CallbackQuery, 
        callback_data: DelCallbackFactory, 
        db: Database,
        i18n: I18nContext,
):
    """Обработчик выполнения задачи."""
    await db.update_task(
        callback_data.user_id, callback_data.task_id, field='done', value=1
    )
    await callback.answer(text=i18n.get('done'))
    await get_callback_answer_of_tasks(
        callback, db, i18n, done=True, key='check-tasks', task_date=date.today()
    )


@router.callback_query(TransferCallbackFactory.filter())
async def process_rescheduling_task(
        callback: CallbackQuery, 
        callback_data: DelCallbackFactory, 
        db: Database,
        i18n: I18nContext,
):
    """Обработчик переноса даты планирования задачи."""
    task = await db.get_task(callback_data.user_id, callback_data.task_id)
    await db.update_task(
        callback_data.user_id,
        callback_data.task_id,
        field='plan_date',
        value=datetime.strptime(task[0][3], '%Y-%m-%d').date() + timedelta(days=1)
    )
    await callback.answer(text=i18n.get('rescheduling'))
    await get_callback_answer_of_tasks(
        callback, db, i18n, done=True, key='check-tasks', task_date=date.today()
    )


@router.callback_query(DelCallbackFactory.filter())
async def process_delete_task(
        callback: CallbackQuery, 
        callback_data: DelCallbackFactory, 
        db: Database,
        i18n: I18nContext,
):
    """Обработчик удаления задачи из БД."""
    await db.delete_task(callback_data.user_id, callback_data.task_id)
    await callback.answer(text=i18n.get('delete'))
    await get_callback_answer_of_tasks(callback, db, i18n)


@router.message(F.text, StateFilter(FSMTask.waiting_task))
async def process_add_task(message: Message, db: Database,  i18n: I18nContext):
    """Обработчик сообщения с задачами."""
    tasks = parsing_task(message)
    case = len(tasks)
    plan_date = date.today() + timedelta(days=1)

    await db.insert_tasks(
        message.from_user.id,
        tasks,
        plan_date=plan_date
    )
    await message.answer(text=i18n.get('task', case=case))


@router.message()
async def send_answer(message: Message, i18n: I18nContext):
    """Обработчик всех остальных сообщений."""
    await message.answer(text=i18n.get('other_answer'))
