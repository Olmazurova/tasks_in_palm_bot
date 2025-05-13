from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_BUTTONS_RU

# Создание кнопок и основных
button_add, button_tasks, button_finish, button_back = [
    InlineKeyboardButton(text=value, callback_data=key)
    for key, value
    in LEXICON_BUTTONS_RU.items()
]

main_kb_builder = InlineKeyboardBuilder()
main_kb_builder.row(button_add, button_tasks, width=2)

# main_keyboard: ReplyKeyboardMarkup = main_kb_builder.as_markup(
#     one_time_keyboard=True,
#     resize_keyboard=True
# )

finish_kb_builder = InlineKeyboardBuilder().row(
    button_finish, button_tasks, width=2
)

# finish_keyboard: ReplyKeyboardMarkup = finish_kb_builder.as_markup(
#     one_time_keyboard=True,
#     resize_keyboard=True
# )

# inline-keyboard

def create_tasks_keyboard(tasks, done=False, state=False) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру из задач пользователя."""
    prefix = '✔' if done else '❌'
    suffix = 'done' if done else 'del'
    kb_builder = InlineKeyboardBuilder()
    for task in tasks:
        kb_builder.row(
            InlineKeyboardButton(
                text=f'{prefix} {task[1]}',
                callback_data=f'{task[0]} {suffix}')
        )
    if not done and not state:
        kb_builder.row(button_back)
    return kb_builder.as_markup()
