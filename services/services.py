import logging
from aiogram import Router
from aiogram.types import Message
# здесь должна быть функция парсинга задач

router = Router()

@router.shutdown()
async def on_shutdown(db):
    """Закрывает соединение с БД."""
    logging.warning('Shutting down..')
    db._conn.close()
    logging.warning("DB Connection closed")


def parsing_task(message: Message):
    """Разбирает сообщение на задачи."""
    tasks = message.text.split('\n')
    return tasks