from aiogram.fsm.state import State, StatesGroup


class FSMAddTask(StatesGroup):
    """Машина состояний, добавляет состояние ожидания задачи."""

    waiting_task = State()
