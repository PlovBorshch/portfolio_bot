from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject
from app.database.requests import set_user  # Твоя функция регистрации


class TrackAllUsersMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # event.from_user дает доступ к юзеру, который прислал апдейт
        user = data.get('event_from_user')

        if user:
            # Просто вызываем set_user.
            # Благодаря onupdate=datetime.now в моделях,
            # время last_seen обновится автоматически при каждом сообщении.
            await set_user(user.id)

        return await handler(event, data)