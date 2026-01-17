import httpx
from typing import Optional, Dict, Any
import json
from .config import Config
from .redis_utils import get_user_state, set_user_state, delete_user_state
from .auth_client import auth_client

class MainAPIClient:
    def __init__(self):
        self.base_url = Config.MAIN_API_URL.rstrip('/')
        self.client = None
    
    async def _get_client(self):
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client
    
    async def _refresh_and_retry(self, chat_id: str, method: str, endpoint: str, **kwargs):
        user_state = get_user_state(chat_id)
        
        if user_state['state'] != 'authorized':
            return None, "Пользователь не авторизован"
        
        refresh_token = user_state.get('refresh_token')
        if not refresh_token:
            delete_user_state(chat_id)
            return None, "Сессия устарела"
        
        
        new_tokens = await auth_client.refresh_access_token(refresh_token)
        
        if not new_tokens or 'access_token' not in new_tokens:
            
            delete_user_state(chat_id)
            return None, "Сессия устарела. Пожалуйста, войдите снова: /login"
        
        
        user_state['access_token'] = new_tokens['access_token']
        user_state['refresh_token'] = new_tokens.get('refresh_token', refresh_token)
        set_user_state(chat_id, 'authorized', user_state)
        
        
        return await self._make_request_with_token(
            chat_id, method, f"{self.base_url}{endpoint}", 
            new_tokens['access_token'], **kwargs
        )
    
    async def _make_request_with_token(self, chat_id: str, method: str, url: str, access_token: str, **kwargs):
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(
                        url,
                        headers=headers,
                        params=kwargs.get('params'),
                        timeout=10.0
                    )
                elif method == "POST":
                    headers["Content-Type"] = "application/json"
                    response = await client.post(
                        url,
                        headers=headers,
                        json=kwargs.get('data'),
                        timeout=10.0
                    )
                elif method == "PUT":
                    headers["Content-Type"] = "application/json"
                    response = await client.put(
                        url,
                        headers=headers,
                        json=kwargs.get('data'),
                        timeout=10.0
                    )
                elif method == "DELETE":
                    if kwargs.get('data'):
                        headers["Content-Type"] = "application/json"
                        response = await client.request(
                            method="DELETE",
                            url=url,
                            headers=headers,
                            json=kwargs.get('data'),
                            timeout=10.0
                        )
                    else:
                        response = await client.delete(url, headers=headers, timeout=10.0)
                else:
                    return None, f"Неподдерживаемый метод: {method}"
                
                return response, None
                
        except httpx.TimeoutException:
            return None, "Таймаут при подключении к серверу"
        except httpx.ConnectError:
            return None, "Не удалось подключиться к серверу"
        except Exception as e:
            return None, f"Ошибка запроса: {e}"
    
    async def make_request(self, method: str, endpoint: str, chat_id: str, **kwargs):
        user_state = get_user_state(chat_id)
        
        if user_state['state'] != 'authorized':
            return None, "Пользователь не авторизован"
        
        access_token = user_state.get('access_token')
        if not access_token:
            return None, "Нет токена доступа"
        
        
        response, error = await self._make_request_with_token(
            chat_id, method, f"{self.base_url}{endpoint}", access_token, **kwargs
        )
        
        if error:
            return None, error
        
        
        if response.status_code == 401:
            
            print(f"[main_api_client] Обнаружена 401 при {method} {endpoint}, обновляем токены...")
            return await self._refresh_and_retry(chat_id, method, endpoint, **kwargs)
        
        
        if response.status_code in [200, 201]:
            try:
                return response.json(), None
            except:
                return response.text, None
        elif response.status_code == 204:
            return {"success": True}, None
        elif response.status_code == 400:
            return None, f"Неверный запрос: {response.text[:200]}"
        elif response.status_code == 403:
            return None, "Недостаточно прав"
        elif response.status_code == 404:
            return None, f"Ресурс не найден: {response.text[:200]}"
        elif response.status_code == 500:
            return None, f"Ошибка сервера: {response.text[:200]}"
        else:
            return None, f"Ошибка {response.status_code}: {response.text[:200]}"
    
    
    async def get_notifications(self, chat_id: str):
        result, error = await self.make_request("GET", "/notifications", chat_id)
        
        if error:
            if "404" in error:
                return []
            return None
        return result if isinstance(result, list) else []
    
    async def delete_notifications(self, chat_id: str):
        result, error = await self.make_request("DELETE", "/notifications", chat_id)
        return not error

main_api_client = MainAPIClient()