from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore

from lexicon.lexicon_ru import LEXICON_BUTTONS_RU


class DoneCallbackFactory(CallbackData, prefix='done'):
    user_id: int
    task_id: int


class DelCallbackFactory(CallbackData, prefix='del'):
    user_id: int
    task_id: int


class TransferCallbackFactory(CallbackData, prefix='transfer'):
    user_id: int
    task_id: int


# Создание кнопок и основных клавиатур
button_add, button_tasks, button_finish, button_back, button_transfer = [
    InlineKeyboardButton(text=value, callback_data=key)
    for key, value
    in LEXICON_BUTTONS_RU.items()
]

main_kb_builder = InlineKeyboardBuilder().row(
    button_add, button_tasks, width=2
)

finish_kb_builder = InlineKeyboardBuilder().row(
    button_finish, button_tasks, width=2
)


def create_tasks_keyboard(
    tasks: list, 
    i18n: FluentRuntimeCore, 
    done: bool = False, 
    state: bool = False
) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру из задач пользователя."""
    prefix = '✅' if done else '❌'
    callback_factory = DoneCallbackFactory if done else DelCallbackFactory
    kb_builder = InlineKeyboardBuilder()
    if done:
        for task in tasks:
            kb_builder.button(
                text=f'{prefix} {task[2]}',
                callback_data=callback_factory(user_id=task[1], task_id=task[0])
            )
            kb_builder.button(
                text=i18n.get('btn_rescheduling'),
                callback_data=TransferCallbackFactory(
                    user_id=task[1], task_id=task[0]
                )
            )
        kb_builder.adjust(2)
    else:
        for task in tasks:
            kb_builder.button(
                text=f'{prefix} {task[2]}',
                callback_data=callback_factory(
                    user_id=task[1],
                    task_id=task[0]
                )
            )
        kb_builder.adjust(1)
    if not done and not state:
        kb_builder.row(button_back)

    return kb_builder.as_markup()
