from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboard_utils import main_kb_builder, create_tasks_keyboard


async def get_answer_of_tasks(callback, db):
    """Отправляет ответ в зависимости от наличия задач."""
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


async def get_id_messages():
    """Возвращает id сообщений добавленных задач."""

