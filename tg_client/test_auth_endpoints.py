import httpx
import asyncio

async def test_auth_endpoints():
    base_url = "http://localhost:8081"
    async with httpx.AsyncClient() as client:
        
        # 1. Тест создания токена входа
        print("1. Создаем login token...")
        response = await client.post(
            f"{base_url}/auth/login/token",
            json={"provider": "default"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('login_token')
            
            # 2. Тест проверки статуса
            print(f"\n2. Проверяем статус для token: {token}")
            response2 = await client.get(
                f"{base_url}/auth/status",
                params={"token": token}
            )
            print(f"   Status: {response2.status_code}")
            print(f"   Response: {response2.text}")

asyncio.run(test_auth_endpoints())