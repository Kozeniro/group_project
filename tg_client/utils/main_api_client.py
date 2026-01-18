import httpx
from typing import Optional, Dict, Any
import json
from .config import Config
from .redis_utils import get_user_state, set_user_state, delete_user_state
from .auth_client import auth_client

class MainAPIClient:
    def __init__(self):
        self.base_url = Config.MAIN_API_URL.rstrip('/')
    
    async def make_request(self, method: str, endpoint: str, chat_id: str, **kwargs):
        user_state = get_user_state(chat_id)
        
        if user_state['state'] != 'authorized':
            return None, "Пользователь не авторизован"
        
        access_token = user_state.get('access_token')
        if not access_token:
            return None, "Нет токена доступа"
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        params=kwargs.get('params'),
                        timeout=10.0
                    )
                elif method == "POST":
                    headers["Content-Type"] = "application/json"
                    response = await client.post(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        json=kwargs.get('data'),
                        timeout=10.0
                    )
                elif method == "PUT":
                    headers["Content-Type"] = "application/json"
                    response = await client.put(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        json=kwargs.get('data'),
                        timeout=10.0
                    )
                elif method == "DELETE":
                    if kwargs.get('data'):
                        headers["Content-Type"] = "application/json"
                        response = await client.request(
                            method="DELETE",
                            url=f"{self.base_url}{endpoint}",
                            headers=headers,
                            json=kwargs.get('data'),
                            timeout=10.0
                        )
                    else:
                        response = await client.delete(
                            f"{self.base_url}{endpoint}",
                            headers=headers,
                            timeout=10.0
                        )
                else:
                    return None, f"Неподдерживаемый метод: {method}"
                
                if response.status_code in [200, 201]:
                    try:
                        return response.json(), None
                    except:
                        return response.text, None
                elif response.status_code == 204:
                    return {"success": True}, None
                elif response.status_code == 401:
                    return None, f"Ошибка авторизации (токен устарел): {response.text[:200]}"
                elif response.status_code == 403:
                    return None, f"Недостаточно прав: {response.text[:200]}"
                elif response.status_code == 404:
                    return None, f"Ресурс не найден: {response.text[:200]}"
                elif response.status_code == 500:
                    return None, f"Ошибка сервера: {response.text[:200]}"
                else:
                    return None, f"Ошибка {response.status_code}: {response.text[:200]}"
                    
        except httpx.TimeoutException:
            return None, "Таймаут при подключении к серверу"
        except httpx.ConnectError:
            return None, "Не удалось подключиться к серверу"
        except Exception as e:
            return None, f"Ошибка запроса: {e}"
    
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