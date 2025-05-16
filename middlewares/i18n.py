from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorRunner


class TranslatorMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        user: User = data.get('event_from_user')
        if user is None:
            return await handler(event, data)

        user_lang = user.language_code
        translator_runner: TranslatorRunner = data.get('t_hub').get_translator_by_locale(
            user_lang, 
            # separator='_',
        )
        data['i18n'] = translator_runner
        return await handler(event, data)
