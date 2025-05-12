from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboard_utils import main_keyboard, create_tasks_keyboard


async def get_answer_of_tasks(callback, db):
    tasks = await db.select_tasks(callback.from_user.id)
    if not tasks:
        await callback.message.answer(
            text=LEXICON_RU['no-tasks'], reply_markup=main_keyboard
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks)
        await callback.message.edit_text(
            text=LEXICON_RU['/tasks_list'],
            reply_markup=tasks_keyboard
        )
