from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_BUTTONS_RU

button_add, button_tasks, button_finish = [
    KeyboardButton(text=value)
    for value
    in LEXICON_BUTTONS_RU.values()
]

main_kb_builder = ReplyKeyboardBuilder()
main_kb_builder.row(button_add, button_tasks, width=2)

main_keyboard: ReplyKeyboardMarkup = main_kb_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)

finish_kb_builder = ReplyKeyboardBuilder().row(
    button_finish, button_tasks, width=2
)

finish_keyboard: ReplyKeyboardMarkup = finish_kb_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)
