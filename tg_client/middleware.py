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
        admin_commands = [
            '/users', '/user_info', '/set_name', '/user_roles', '/block_user',
            '/create_course', '/update_course', '/delete_course', '/course_students',
            '/add_to_course', '/remove_from_course', '/add_test', '/remove_test',
            '/set_test_active', '/test_results', '/create_question', '/add_to_test'
        ]
        if event.text and any(event.text.startswith(cmd) for cmd in admin_commands):
            chat_id = str(event.chat.id)
            user_state = get_user_state(chat_id)
            
            if user_state['state'] != 'authorized':
                await event.answer("Вы не авторизованы. Используйте /login")
                return
            
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
                access_token = user_state.get('access_token')
                if access_token:
                    decoded = jwt.decode(access_token, options={"verify_signature": False})
                    roles = decoded.get('roles', [])
                    permissions = decoded.get('permissions', [])
                    
                    if 'admin' not in roles and 'teacher' not in roles:
                        await event.answer("Эта команда доступна только администраторам и учителям")
                        return
            except:
                await event.answer("Ошибка авторизации.")
                return
        
        data['user_state'] = user_state
        return await handler(event, data)