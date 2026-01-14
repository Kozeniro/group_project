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
        
        if user_state['state'] == 'unknown':
            if not event.text.startswith('/login'):
                await event.answer("Вы не авторизованы. Используйте /login")
                return
        
        elif user_state['state'] == 'authorized':
            access_token = user_state.get('access_token')
            refresh_token = user_state.get('refresh_token')
            
            if not access_token or not refresh_token:
                await event.answer("Ошибка сессии. Используйте /login")
                return
            
            try:
                decoded = jwt.decode(access_token, options={"verify_signature": False})
                exp = decoded.get('exp', 0)
                if datetime.now().timestamp() > exp:
                    new_tokens = await auth_client.refresh_access_token(refresh_token)
                    
                    if new_tokens and 'access_token' in new_tokens:
                        user_state['access_token'] = new_tokens['access_token']
                        user_state['refresh_token'] = new_tokens.get('refresh_token', refresh_token)
                    else:
                        await event.answer("Сессия истекла. Используйте /login")
                        return
            except:
                await event.answer("Ошибка авторизации.")
                return
        
        data['user_state'] = user_state
        return await handler(event, data)