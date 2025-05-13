from aiogram.fsm.state import State, StatesGroup


class FSMTask(StatesGroup):
    """Машина состояний, добавляет состояние ожидания задачи."""

    start = State()
    help = State()
    waiting_task = State()
    task_list = State()
    check = State()
