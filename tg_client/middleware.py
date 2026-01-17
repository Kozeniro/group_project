from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from utils.redis_utils import get_user_state
from utils.auth_client import auth_client
import jwt
from datetime import datetime

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        chat_id = str(event.chat.id)
        user_state = get_user_state(chat_id)                    
        if user_state['state'] == 'authorized':
            access_token = user_state.get('access_token')
            refresh_token = user_state.get('refresh_token')
            
            if not access_token or not refresh_token:
                await event.answer("Ошибка сессии. Используйте /login")
                return

        data['user_state'] = user_state
        return await handler(event, data)