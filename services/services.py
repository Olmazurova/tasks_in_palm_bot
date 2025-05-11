import logging
from aiogram import Router
# здесь должна быть функция парсинга задач

router = Router()

@router.shutdown()
async def on_shutdown(db):
    """Закрывает соединение с БД."""
    logging.warning('Shutting down..')
    db._conn.close()
    logging.warning("DB Connection closed")
