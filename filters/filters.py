from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class IsDelTaskCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return (
                callback.data.endswith('del')
                and callback.data.split()[0].isdigit()
        )


class IsDoneTaskCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return (
                callback.data.endswith('done')
                and callback.data.split()[0].isdigit()
        )
