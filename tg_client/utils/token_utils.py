import httpx
from typing import Optional, Dict, Any, Tuple
from .redis_utils import get_user_state, set_user_state, delete_user_state
from .auth_client import auth_client
from .main_api_client import main_api_client
from .config import Config

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
    
    access_token = user_state.get('access_token')
    
    if not access_token:
        return None, "Нет access token"
    
    base_url = Config.MAIN_API_URL.rstrip('/')
    
    try:
        response = await _make_request(method, f"{base_url}{endpoint}", access_token, **kwargs)
        
        if response.status_code == 200:
            if not response.text or response.text.strip() == '':
                return {"success": True}, None
            
            try:
                return response.json(), None
            except:
                return response.text, None
                
        elif response.status_code == 201:
            try:
                return response.json(), None
            except:
                return {"success": True, "message": response.text}, None
                
        elif response.status_code == 204:
            return {"success": True}, None
            
        elif response.status_code == 400:
            error_text = response.text[:200] if response.text else "Bad Request"
            return None, f"Неверный запрос: {error_text}"
            
        elif response.status_code == 401:
            refreshed = await refresh_tokens(chat_id)
            if refreshed:
                user_state = get_user_state(chat_id)
                response = await _make_request(method, f"{base_url}{endpoint}", user_state.get('access_token'), **kwargs)
                if response.status_code in [200, 201, 204]:
                    return {"success": True}, None
            
            return None, "Ошибка авторизации"
            
        elif response.status_code == 403:
            return None, "Недостаточно прав"
            
        elif response.status_code == 404:
            return None, "Ресурс не найден"
            
        elif 500 <= response.status_code < 600:
            error_text = response.text[:200] if response.text else "Internal Server Error"
            return None, f"Ошибка сервера: {error_text}"
            
        else:
            return None, f"Ошибка: {response.status_code}"
            
    except Exception as e:
        print(f"Error in make_authorized_request: {e}")
        return None, f"Ошибка подключения: {e}"
    

async def _make_request(method: str, url: str, access_token: str, **kwargs):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            response = await client.get(
                url,
                headers=headers,
                params=kwargs.get('params'),
                timeout=10.0
            )
        elif method == "POST":
            response = await client.post(
                url,
                headers=headers,
                json=kwargs.get('data'),
                timeout=10.0
            )
        elif method == "PUT":
            response = await client.put(
                url,
                headers=headers,
                json=kwargs.get('data'),
                timeout=10.0
            )
        elif method == "DELETE":
            response = await client.delete(
                url,
                headers=headers,
                timeout=10.0
            )
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response