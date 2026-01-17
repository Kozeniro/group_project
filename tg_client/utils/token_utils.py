import httpx
import json
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


async def make_authorized_request(chat_id: str, method: str, endpoint: str, **kwargs):
    
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        return None, "Пользователь не авторизован"
    
    access_token = user_state.get('access_token')
    refresh_token = user_state.get('refresh_token')
    
    if not access_token or not refresh_token:
        return None, "Нет токенов доступа"
    
    base_url = Config.MAIN_API_URL.rstrip('/')
    
    print(f"\n[make_authorized_request] Начало: {method} {endpoint}")
    print(f"   Chat ID: {chat_id}")
    print(f"   Access token: {access_token[:30]}...")
    print(f"   Refresh token: {refresh_token[:30]}...")
    
    
    result, error = await _make_request_with_token(chat_id, method, f"{base_url}{endpoint}", access_token, **kwargs)
    
    
    if error and ("401" in str(error) or "Ошибка авторизации" in str(error)):
        print(f"[make_authorized_request] Обнаружена 401! Обновление токенов...")
        
        
        new_tokens = await auth_client.refresh_access_token(refresh_token)
        
        if new_tokens and 'access_token' in new_tokens:
            print(f"[make_authorized_request] Токены обновлены успешно!")            
            
            user_state['access_token'] = new_tokens['access_token']
            user_state['refresh_token'] = new_tokens.get('refresh_token', refresh_token)
            set_user_state(chat_id, 'authorized', user_state)            
            
            new_access_token = new_tokens['access_token']
            result, error = await _make_request_with_token(chat_id, method, f"{base_url}{endpoint}", new_access_token, **kwargs)
            
            if not error:
                print(f"[make_authorized_request] Запрос успешен после обновления токена!")
                return result, None
            else:
                print(f"[make_authorized_request] Ошибка даже после обновления токена: {error}")
                return None, error
        else:
            print(f"[make_authorized_request] Не удалось обновить токены!")
            
            delete_user_state(chat_id)
            return None, "Сессия устарела. Пожалуйста, войдите снова: /login"
    
    print(f"[make_authorized_request] Результат: {'Успех' if not error else f'Ошибка: {error}'}")
    return result, error

async def _make_request_with_token(chat_id: str, method: str, url: str, access_token: str, **kwargs):    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print(f"   Запрос: {method} {url}")
    if kwargs.get('data'):
        print(f"   Данные: {kwargs['data']}")
    
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
                        content=json.dumps(kwargs['data']),
                        timeout=10.0
                    )
                else:
                    response = await client.delete(url, headers=headers, timeout=10.0)
            else:
                return None, f"Неподдерживаемый метод: {method}"
            
            print(f"   Ответ: {response.status_code}")
            if response.text:
                print(f"   Тело: {response.text[:200]}")
            
            if response.status_code in [200, 201]:
                try:
                    return response.json(), None
                except:
                    return response.text, None
            elif response.status_code == 204:
                return {"success": True}, None
            elif response.status_code == 400:
                return None, f"Неверный запрос: {response.text[:200]}"
            elif response.status_code == 401:
                return None, "Ошибка авторизации (токен устарел или неверный)"
            elif response.status_code == 403:
                return None, "Недостаточно прав"
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