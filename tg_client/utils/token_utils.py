import httpx
from typing import Optional, Dict, Any, Tuple
from .redis_utils import get_user_state, set_user_state, delete_user_state
from .auth_client import auth_client
from .main_api_client import main_api_client

async def refresh_tokens(chat_id: str) -> Optional[Dict[str, Any]]:
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        return None
    
    access_token = user_state.get('access_token')
    refresh_token = user_state.get('refresh_token')
    
    if not access_token or not refresh_token:
        return None
    
    response = await main_api_client.make_request(
        "GET", "/api/users/me", access_token
    )
    
    if response and response.status_code == 401:
        new_tokens = await auth_client.refresh_access_token(refresh_token)
        
        if new_tokens and 'access_token' in new_tokens:
            user_state['access_token'] = new_tokens['access_token']
            user_state['refresh_token'] = new_tokens.get('refresh_token', refresh_token)
            set_user_state(chat_id, 'authorized', user_state)
            return user_state
        else:
            await auth_client.logout(refresh_token)
            delete_user_state(chat_id)
            return None
    
    return user_state

async def make_authorized_request(chat_id: str, method: str, endpoint: str, **kwargs) -> Tuple[Optional[Any], Optional[str]]:
    user_state = get_user_state(chat_id)
    
    if not user_state or user_state['state'] != 'authorized':
        return None, "Пользователь не авторизован"
    
    user_state = await refresh_tokens(chat_id)
    
    if not user_state:
        return None, "Ошибка обновления токенов. Пожалуйста, авторизуйтесь заново."
    
    access_token = user_state.get('access_token')
    
    if endpoint == "/api/users/me":
        user_id = user_state.get('user_id')
        if not user_id:
            return None, "Не удалось получить ID пользователя"
        endpoint = f"/api/users/{user_id}"
    
    response = await main_api_client.make_request(method, endpoint, access_token, **kwargs)
    
    if response.status_code == 200:
        return response.json(), None
    elif response.status_code == 403:
        return None, "Недостаточно прав"
    elif response.status_code == 401:
        return None, "Ошибка авторизации"
    elif response.status_code == 404:
        return None, "Ресурс не найден"
    elif response.status_code == 400:
        return None, "Неверный запрос"
    else:
        return None, f"Ошибка: {response.status_code}"