import httpx
from .config import Config

class MainAPIClient:
    def __init__(self):
        self.base_url = Config.MAIN_API_URL.rstrip('/')
        self.client = None
    
    async def _get_client(self):
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client
    
    async def make_request(self, method: str, endpoint: str, access_token: str, **kwargs):
        client = await self._get_client()
        headers = {"Authorization": f"Bearer {access_token}"}        
        
        if method == "GET":
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                params=kwargs.get('params')
            )
        elif method == "POST":
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=kwargs.get('data')
            )
        elif method == "PUT":
            response = await client.put(
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=kwargs.get('data')
            )
        elif method == "DELETE":
            response = await client.delete(
                f"{self.base_url}{endpoint}",
                headers=headers
            )        
        return response
    
    
    async def get_tests(self, access_token: str):
        response = await self.make_request("GET", "/api/tests", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_courses(self, access_token: str):
        response = await self.make_request("GET", "/api/course", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_notifications(self, access_token: str):
        response = await self.make_request("GET", "/notifications", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def delete_notifications(self, access_token: str):
        response = await self.make_request("DELETE", "/notifications", access_token)
        return response.status_code == 200 if response else False

main_api_client = MainAPIClient()