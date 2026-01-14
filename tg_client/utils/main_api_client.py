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
    
    #Пользователи
    async def get_all_users(self, access_token: str):
        response = await self.make_request("GET", "/api/users", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_user_name(self, access_token: str, user_id: str):
        response = await self.make_request("GET", f"/api/users/{user_id}/name", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def update_user_name(self, access_token: str, user_id: str, new_name: str):
        response = await self.make_request("PUT", f"/api/users/{user_id}/name", access_token, 
                                          data={"new_name": new_name})
        return response
    
    async def get_user_info(self, access_token: str, user_id: str, info_type: str):
        response = await self.make_request("GET", f"/api/users/{user_id}/info", access_token,
                                          params={"info_type": info_type})
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_user_roles(self, access_token: str, user_id: str):
        response = await self.make_request("GET", f"/api/users/{user_id}/roles", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def set_user_roles(self, access_token: str, user_id: str, roles: list):
        response = await self.make_request("POST", f"/api/users/{user_id}/roles", access_token,
                                          data={"roles": roles})
        return response
    
    async def check_user_blocked(self, access_token: str, user_id: str):
        response = await self.make_request("GET", f"/api/users/{user_id}/blocked", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def set_user_blocked(self, access_token: str, user_id: str, blocked: bool):
        response = await self.make_request("POST", f"/api/users/{user_id}/blocked", access_token,
                                          data={"blocked": blocked})
        return response
    
    #Курсы
    async def get_all_courses(self, access_token: str):
        response = await self.make_request("GET", "/api/course", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_course_info(self, access_token: str, course_id: str):
        response = await self.make_request("GET", f"/api/course/{course_id}/info", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def update_course_info(self, access_token: str, course_id: str, name: str, description: str):
        response = await self.make_request("PUT", f"/api/course/{course_id}/info", access_token,
                                          data={"name": name, "description": description})
        return response
    
    async def get_course_tests(self, access_token: str, course_id: str):
        response = await self.make_request("GET", f"/api/course/{course_id}/tests", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def is_test_active(self, access_token: str, course_id: str, test_id: str):
        response = await self.make_request("GET", f"/api/course/{course_id}/tests/{test_id}/activity", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def set_test_active(self, access_token: str, course_id: str, test_id: str, activity: bool):
        response = await self.make_request("POST", f"/api/course/{course_id}/tests/{test_id}/activity", access_token,
                                          data={"activity": activity})
        return response
    
    async def add_test(self, access_token: str, course_id: str, test_name: str):
        response = await self.make_request("POST", f"/api/course/{course_id}/tests", access_token,
                                          data={"test_name": test_name})
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def remove_test(self, access_token: str, course_id: str, test_id: str):
        response = await self.make_request("DELETE", f"/api/course/{course_id}/tests/{test_id}", access_token)
        return response
    
    async def get_course_students(self, access_token: str, course_id: str):
        response = await self.make_request("GET", f"/api/course/{course_id}/students", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def add_user_to_course(self, access_token: str, course_id: str, user_id: str):
        response = await self.make_request("POST", f"/api/course/{course_id}/students", access_token,
                                          data={"user_id": user_id})
        return response
    
    async def remove_user_from_course(self, access_token: str, course_id: str, student_id: str):
        response = await self.make_request("DELETE", f"/api/course/{course_id}/students/{student_id}", access_token)
        return response
    
    async def create_course(self, access_token: str, name: str, description: str, instructor_id: str):
        response = await self.make_request("POST", "/api/course", access_token,
                                          data={"name": name, "description": description, "instructor_id": instructor_id})
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def delete_course(self, access_token: str, course_id: str):
        response = await self.make_request("DELETE", f"/api/course/{course_id}", access_token)
        return response
    
    #Вопросы
    async def get_all_questions(self, access_token: str):
        response = await self.make_request("GET", "/api/questions", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_question_info(self, access_token: str, question_id: str, version: int = None):
        params = {}
        if version is not None:
            params["version"] = version
        response = await self.make_request("GET", f"/api/questions/{question_id}", access_token,
                                          params=params)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def update_question(self, access_token: str, question_id: str, name: str, text: str, 
                             options: dict, correct_option: int):
        response = await self.make_request("PUT", f"/api/questions/{question_id}", access_token,
                                          data={
                                              "name": name,
                                              "text": text,
                                              "options": options,
                                              "correct_option": correct_option
                                          })
        return response
    
    async def create_question(self, access_token: str, name: str, text: str, options: dict, correct_option: int):
        response = await self.make_request("POST", "/api/questions", access_token,
                                          data={
                                              "name": name,
                                              "text": text,
                                              "options": options,
                                              "correct_option": correct_option
                                          })
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def delete_question(self, access_token: str, question_id: str):
        response = await self.make_request("DELETE", f"/api/questions/{question_id}", access_token)
        return response
    
    #тесты
    async def get_all_tests(self, access_token: str):
        response = await self.make_request("GET", "/api/tests", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def remove_question_from_test(self, access_token: str, test_id: str, question_id: str):
        response = await self.make_request("DELETE", f"/api/tests/{test_id}/questions/{question_id}", access_token)
        return response
    
    async def add_question_to_test(self, access_token: str, test_id: str, question_id: str):
        response = await self.make_request("POST", f"/api/tests/{test_id}/questions", access_token,
                                          data={"question_id": question_id})
        return response
    
    async def set_question_order(self, access_token: str, test_id: str, question_ids: list):
        response = await self.make_request("PUT", f"/api/tests/{test_id}/questions", access_token,
                                          data={"question_ids": question_ids})
        return response
    
    async def get_users_completed_test(self, access_token: str, test_id: str):
        response = await self.make_request("GET", f"/api/tests/{test_id}/users", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_users_scores(self, access_token: str, test_id: str):
        response = await self.make_request("GET", f"/api/tests/{test_id}/scores", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_users_answers(self, access_token: str, test_id: str):
        response = await self.make_request("GET", f"/api/tests/{test_id}/answers", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    #Попытки
    async def create_attempt(self, access_token: str, user_id: str, test_id: str):
        response = await self.make_request("POST", "/api/attempt", access_token,
                                          data={"user_id": user_id, "test_id": test_id})
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def update_answer_in_attempt(self, access_token: str, attempt_id: str, answer_id: str, answer_option: int):
        response = await self.make_request("PUT", f"/api/attempt/{attempt_id}", access_token,
                                          data={"answer_id": answer_id, "answer_option": answer_option})
        return response
    
    async def finish_attempt(self, access_token: str, attempt_id: str):
        response = await self.make_request("DELETE", f"/api/attempt/{attempt_id}", access_token)
        return response
    
    async def get_attempt_info(self, access_token: str, user_id: str, test_id: str):
        response = await self.make_request("GET", "/api/attempt", access_token,
                                          params={"user_id": user_id, "test_id": test_id})
        if response and response.status_code == 200:
            return response.json()
        return None
    
    #Вопросы
    async def create_answer(self, access_token: str, attempt_id: str, question_id: str):
        response = await self.make_request("POST", "/api/answers", access_token,
                                          data={"attempt_id": attempt_id, "question_id": question_id})
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def get_answer_info(self, access_token: str, answer_id: str):
        response = await self.make_request("GET", f"/api/answers/{answer_id}", access_token)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    async def update_answer(self, access_token: str, answer_id: str, answer_option: int):
        response = await self.make_request("PUT", f"/api/answers/{answer_id}", access_token,
                                          data={"answer_option": answer_option})
        return response
    
    async def delete_answer(self, access_token: str, answer_id: str):
        response = await self.make_request("DELETE", f"/api/answers/{answer_id}", access_token)
        return response
    
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