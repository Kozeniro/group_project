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
    
    async def register_user(self, email: str, password: str) -> Dict:
        client = await self._get_client()
        
        response = await client.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "password": password},
            timeout=10.0
        )
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}
    
    async def login_user(self, email: str, password: str) -> Dict:
        client = await self._get_client()
        
        response = await client.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password},
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}

    async def create_login_token(self) -> Dict:
        client = await self._get_client()
        
        response = await client.post(
            f"{self.base_url}/auth/login/token",
            json={},
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}

    async def get_code_for_login(self, login_token: str) -> Dict:
        client = await self._get_client()
        
        response = await client.get(
            f"{self.base_url}/auth/login/code",
            params={"state": login_token},
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}

    async def verify_code_with_refresh_token(self, code: str, refresh_token: str) -> Dict:
        client = await self._get_client()
        
        response = await client.post(
            f"{self.base_url}/auth/login/code/verify",
            json={"code": code, "refresh_token": refresh_token},
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}

    async def check_login_status(self, login_token: str) -> Dict:
        client = await self._get_client()
        
        response = await client.get(
            f"{self.base_url}/auth/status",
            params={"login_token": login_token},
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}

    async def get_github_auth_url(self, login_token: str):
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/auth/login/github",
            params={"token": login_token},
            follow_redirects=False,
            timeout=10.0
        )
        
        if response.status_code == 302:
            return response.headers.get('Location')
        else:
            return None
    
    async def get_yandex_auth_url(self, login_token: str):
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/auth/login/yandex",
            params={"token": login_token},
            follow_redirects=False,
            timeout=10.0
        )
        
        if response.status_code == 302:
            return response.headers.get('Location')
        else:
            return None
    
    async def refresh_access_token(self, refresh_token: str):
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}
    
    async def logout(self, refresh_token: str):
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/auth/logout",
            json={"refresh_token": refresh_token},
            timeout=10.0
        )
        
        return response.status_code == 200

auth_client = AuthClient()