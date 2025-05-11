import logging
from aiogram import Router
# здесь должна быть функция парсинга задач

router = Router()

@router.shutdown()
async def on_shutdown(dispatcher):
    """Закрывает соединение с БД."""
    logging.warning('Shutting down..')
    dispatcher.db._conn.close()
    logging.warning("DB Connection closed")
