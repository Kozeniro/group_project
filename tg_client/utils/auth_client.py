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
           
    
    async def create_login_token(self) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        
        response = await client.post(
            f"{self.base_url}/auth/login/token",
            json={},
            timeout=10.0
        )        
        data = response.json()
        return data
        

    async def get_code_for_token(self, login_token: str) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
    
        response = await client.get(
            f"{self.base_url}/auth/login/code",
            params={"state": login_token},
            timeout=10.0
        )                        
        data = response.json()
        return data
    


    async def verify_code(self, code: str) -> Dict:
        client = await self._get_client()       
        
        print(f"DEBUG: Verifying code: {code}")
        response = await client.get(
            f"{self.base_url}/auth/verify",
            params={"code": code},
            timeout=10.0
        )
        
        print(f"DEBUG: Verify code response: {response.status_code}")
        print(f"DEBUG: Response body: {response.text}")
                
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }

    
    async def get_github_auth_url(self, login_token: str):
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/auth/login/github",
            params={"token": login_token},
            follow_redirects=False,
            timeout=10.0
        )        
        return response.headers.get('Location')

    
    async def get_yandex_auth_url(self, login_token: str):
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/auth/login/yandex",
            params={"token": login_token},
            follow_redirects=False,
            timeout=10.0
        )
        return response.headers.get('Location')
    
    
    async def check_login_status(self, login_token: str) -> Dict:
        client = await self._get_client()
        
        print(f"DEBUG: Checking login status for token: {login_token}")
        response = await client.get(
            f"{self.base_url}/auth/status",
            params={"login_token": login_token},
            timeout=10.0
        )
        
        print(f"DEBUG: Status check response: {response.status_code}")
        print(f"DEBUG: Response body: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }

    async def verify_code(self, code: str) -> Dict:
        client = await self._get_client()       
        
        print(f"DEBUG: Verifying code: {code}")
        response = await client.get(
            f"{self.base_url}/auth/verify",
            params={"code": code},
            timeout=10.0
        )
        
        print(f"DEBUG: Verify code response: {response.status_code}")
        print(f"DEBUG: Response body: {response.text}")
                
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
        
    
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
            json={"refresh_token": refresh_token},
            timeout=10.0
        )            
        return response.status_code == 200


auth_client = AuthClient()
