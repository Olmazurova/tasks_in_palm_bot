from datetime import date, timedelta

from keyboards.keyboard_utils import create_tasks_keyboard, main_kb_builder


async def get_callback_answer_of_tasks(
    callback, 
    db, 
    i18n, 
    done=False, 
    key='tasks_list', 
    task_date=date.today() + timedelta(days=1),
):
    """Отправляет ответ на нажатие кнопки в зависимости от наличия задач."""
    tasks = await db.select_tasks(callback.from_user.id, plan_date=task_date)
    if not tasks:
        await callback.message.edit_text(
            text=i18n.get('no-tasks', case=1),
            reply_markup=main_kb_builder.as_markup(),
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, i18n, done=done)
        await callback.message.edit_text(
            text=i18n.get(key, date=task_date),
            reply_markup=tasks_keyboard,
        )


async def get_message_answer_of_tasks(message, db, i18n):
    """Отправляет ответ на команду в зависимости от наличия задач."""
    tasks = await db.select_tasks(message.from_user.id)
    if not tasks:
        await message.answer(
            text=i18n.get('no-tasks', case=1),
            reply_markup=main_kb_builder.as_markup(),
        )
    else:
        tasks_keyboard = create_tasks_keyboard(tasks, i18n, state=True)
        await message.answer(
            text=i18n.get('tasks_list', date=date.today() + timedelta(days=1)),
            reply_markup=tasks_keyboard,
        )
