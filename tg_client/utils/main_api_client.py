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
        headers = {"Authorization": f"Bearer {access_token[:20]}..."}
        
        print(f"DEBUG main_api: Making {method} request to {endpoint}")
        print(f"DEBUG main_api: Headers: {headers}")
        
        try:
            if method == "GET":
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    params=kwargs.get('params'),
                    timeout=10.0
                )
            elif method == "POST":
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    json=kwargs.get('data'),
                    timeout=10.0
                )
            elif method == "PUT":
                response = await client.put(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    json=kwargs.get('data'),
                    timeout=10.0
                )
            elif method == "DELETE":
                response = await client.delete(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    timeout=10.0
                )
            
            print(f"DEBUG main_api: Response status: {response.status_code}")
            print(f"DEBUG main_api: Response body: {response.text[:200]}")
            
            return response
        except Exception as e:
            print(f"DEBUG main_api: Exception: {e}")
            raise
    
    
    #Уведомления
    async def get_notifications(self, access_token: str):
        response = await self.make_request("GET", "/notifications", access_token)
        if response and response.status_code == 200:
            return response.json()
        elif response and response.status_code == 404:
            return []
        return []
    
    async def delete_notifications(self, access_token: str):
        response = await self.make_request("DELETE", "/notifications", access_token)
        return response.status_code == 200 if response else False

main_api_client = MainAPIClient()