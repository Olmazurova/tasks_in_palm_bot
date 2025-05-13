from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboard_utils import main_kb_builder, create_tasks_keyboard


async def get_callback_answer_of_tasks(callback, db):
    """Отправляет ответ на нажатие кнопки в зависимости от наличия задач."""
    tasks = await db.select_tasks(callback.from_user.id)
    if not tasks:
        await callback.message.edit_text(
            text=LEXICON_RU['no-tasks'],
            reply_markup=main_kb_builder.as_markup(),
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks)
        await callback.message.edit_text(
            text=LEXICON_RU['/tasks_list'],
            reply_markup=tasks_keyboard,
        )


async def get_message_answer_of_tasks(message, db):
    """Отправляет ответ на команду в зависимости от наличия задач."""
    tasks = await db.select_tasks(message.from_user.id)
    if not tasks:
        await message.answer(
            text=LEXICON_RU['no-tasks'],
            reply_markup=main_kb_builder.as_markup(),
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, state=True)
        await message.answer(
            text=LEXICON_RU['/tasks_list'],
            reply_markup=tasks_keyboard,
        )
