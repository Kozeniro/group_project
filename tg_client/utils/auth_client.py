import httpx
from typing import Optional, Dict, Any
from .config import Config

class AuthClient:
    def __init__(self):
        self.base_url = Config.AUTH_SERVER_URL.rstrip('/')
        self.client = None
    
    async def _get_client(self):
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={'Content-Type': 'application/json'}
            )
        return self.client
    
    async def create_login_token(self, provider: str = "default") -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/auth/login/token",
            json={"provider": provider}
        )
        data = response.json()
        token = data.get('login_token')
        return {"token": token, "full_response": data}    
    
    async def get_github_auth_url(self, login_token: str):
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/auth/login/github",
            params={"token": login_token}
        )        
        return response.headers.get('Location')

    
    async def get_yandex_auth_url(self, login_token: str):
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/auth/login/yandex",
            params={"token": login_token}
        )
        return response.headers.get('Location')
    
    async def check_login_status(self, login_token: str):
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/auth/status",
            params={"token": login_token}
        )
        return response.json()
    
    async def login_with_code(self, code: str, login_token: str):
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/auth/login",
            json={
                "code": code,
                "token": login_token
            }
        )
        return response.json()
    
    async def refresh_access_token(self, refresh_token: str):
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        return response.json()
    
    async def logout(self, refresh_token: str):
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/auth/logout",
            json={"refresh_token": refresh_token}
        )            
        return response.status_code == 200
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/protected/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()
    
    async def close(self):
        if self.client:
            await self.client.aclose()


auth_client = AuthClient()