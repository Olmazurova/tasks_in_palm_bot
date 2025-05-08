from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
# from create_dp import dp
from keyboards.keyboard_utils import main_keyboard, finish_keyboard
from lexicon.lexicon_ru import LEXICON_RU, LEXICON_BUTTONS_RU
from states.states import FSMAddTask

router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.set_state(state=None)
    await message.answer(text=LEXICON_RU['/start'], reply_markup=main_keyboard)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message, state: FSMContext):
    await state.set_state(state=None)
    await message.answer(text=LEXICON_RU['/help'], reply_markup=main_keyboard)


# /add-task
@router.message(
    F.text == LEXICON_BUTTONS_RU['/add-task'],
    StateFilter(default_state)
)
async def process_btn_add_task(message: Message, state: FSMContext):
    await state.set_state(FSMAddTask.waiting_task)
    await message.answer(
        text=LEXICON_RU['/add-task'], reply_markup=finish_keyboard
    )

# /tasks-list
@router.message(F.text == LEXICON_BUTTONS_RU['/tasks-list'])
async def process_btn_tasks_list(message: Message, state: FSMContext):
    await state.set_state(state=None)
    await message.answer(
        text=LEXICON_RU['/tasks-list'], reply_markup=finish_keyboard
    )  # клавиатуру заменить на инлайн клавиатуру задач.


# /finish-planning
@router.message(F.text == LEXICON_BUTTONS_RU['/finish-planning'])
async def process_btn_finish_task(message: Message, state: FSMContext):
    await state.set_state(state=None)
    await message.answer(
        text=LEXICON_RU['/finish-planning'], reply_markup=main_keyboard
    )


# done
@router.callback_query(F.data.in_(['done']))
async def process_done_task(callback: CallbackQuery):
    # удаляем задачу из списка, FSM -  default
    await callback.message.reply(reply_markup=main_keyboard)  # ????
    await callback.answer(text=LEXICON_RU['done'])

# rescheduling
@router.callback_query(F.data.in_(['rescheduling']))
async def process_rescheduling_task(callback: CallbackQuery):
    # удаляем задачу из списка, FSM -  default
    await callback.message.reply(reply_markup=main_keyboard) # ????
    await callback.answer(text=LEXICON_RU['rescheduling'])

# delete
@router.callback_query(F.data.in_(['delete']))
async def process_delete_task(callback: CallbackQuery):
    # удаляем задачу из списка, FSM -  default
    await callback.message.reply(reply_markup=main_keyboard) # ????
    await callback.answer(text=LEXICON_RU['delete'])


# task
@router.message(F.text, StateFilter(FSMAddTask.waiting_task))
async def process_add_task(message: Message):
    # парсим сообщение и добавляем задачи в список, FSM - waiting_task
    await message.answer(text=LEXICON_RU['task'])


# Этот хендлер обрабатывает все остальные сообщения
@router.message()
async def send_answer(message: Message):
    await message.answer(text=LEXICON_RU['other_answer'])
