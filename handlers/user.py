from datetime import timedelta

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
# from create_dp import dp
from keyboards.keyboard_utils import (main_keyboard, finish_keyboard,
                                      create_tasks_keyboard)
from lexicon.lexicon_ru import LEXICON_RU, LEXICON_BUTTONS_RU
from states.states import FSMAddTask

router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, db):
    """Обработчик команды /start."""
    # Проверяем есть ли пользователь в БД, если нет - заносим туда
    if db.select_user(message.from_user.id) is None:
        db.insert_user(message.from_user)
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
async def process_btn_tasks_list(message: Message, state: FSMContext, db):
    """Обработчик команды /tasks-list."""
    await state.set_state(state=None)
    tasks = db.select_tasks(message.from_user.id)
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
async def process_done_task(callback: CallbackQuery, state: FSMContext, db):
    """Обработчик выполнения задачи."""
    await state.set_state(state=None)
    db.update_task(callback.from_user.id, callback.data, field='done', value=1)
    await callback.answer(text=LEXICON_RU['done'])
    tasks = db.select_tasks(callback.from_user.id)
    if not tasks:
        await callback.message.reply(
            text=LEXICON_RU['no-tasks'], reply_markup=main_keyboard
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks)
        await callback.message.edit_text(
            text=LEXICON_RU['/tasks-list'], reply_markup=tasks_keyboard
        )


# rescheduling
@router.callback_query(F.data.in_(['rescheduling']))
async def process_rescheduling_task(callback: CallbackQuery, db):
    """Обработчик переноса даты планирования задачи."""
    task = db.get_task(callback.from_user.id, callback.data)
    db.update_task(
        callback.from_user.id,
        callback.data,
        field='plan_date',
        value=task.plan_date + timedelta(days=1)
    )
    await callback.answer(text=LEXICON_RU['rescheduling'])
    tasks = db.select_tasks(callback.from_user.id)
    if not tasks:
        await callback.message.reply(
            text=LEXICON_RU['no-tasks'], reply_markup=main_keyboard
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks)
        await callback.message.edit_text(
            text=callback.message.text,
            reply_markup=tasks_keyboard
        )


# delete
@router.callback_query(F.data.in_(['delete']))
async def process_delete_task(callback: CallbackQuery, state: FSMContext, db):
    """Обработчик удаления задачи из БД."""
    await state.set_state(state=None)
    db.delete_task(callback.from_user.id, callback.data)
    await callback.answer(text=LEXICON_RU['delete'])
    tasks = db.select_tasks(callback.from_user.id)
    if not tasks:
        await callback.message.reply(
            text=LEXICON_RU['no-tasks'], reply_markup=main_keyboard
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks)
        await callback.message.edit_text(
            text=callback.message.text,
            reply_markup=tasks_keyboard
        )


# task
@router.message(F.text, StateFilter(FSMAddTask.waiting_task))
async def process_add_task(message: Message):
    # парсим сообщение и добавляем задачи в список, FSM - waiting_task
    await message.answer(text=LEXICON_RU['task'])


# Этот хендлер обрабатывает все остальные сообщения
@router.message()
async def send_answer(message: Message):
    await message.answer(text=LEXICON_RU['other_answer'])
