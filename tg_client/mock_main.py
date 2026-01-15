from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime
import json
import random

app = FastAPI(title="Mock Main Module API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mock_db = {
    "users": {},
    "courses": {},
    "tests": {},
    "questions": {},
    "attempts": {},
    "answers": {},
}

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = authorization[7:]
    
    if not token or len(token) < 10:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        if "user_" in token:
            user_id = token.split("_")[1] if len(token.split("_")) > 1 else "unknown"
        else:
            user_id = "unknown"
        
        return {"user_id": user_id, "token": token}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_or_create_user(user_id: str, name: str = "Пользователь"):
    if user_id not in mock_db["users"]:
        mock_db["users"][user_id] = {
            "id": user_id,
            "name": name,
            "email": f"user_{user_id}@example.com",
            "roles": ["student"],
            "courses": [],
            "tests": [],
            "scores": [],
            "created_at": datetime.now().isoformat()
        }
    return mock_db["users"][user_id]

@app.get("/api/users")
async def get_all_users(auth: Dict = Depends(verify_token)):
    users = []
    for user_id, user_data in mock_db["users"].items():
        users.append({
            "id": user_data["id"],
            "name": user_data["name"]
        })
    return users

@app.get("/api/users/{user_id}/name")
async def get_user_name(user_id: str, auth: Dict = Depends(verify_token)):
    if user_id in mock_db["users"]:
        return {"name": mock_db["users"][user_id]["name"]}
    else:
        user = get_or_create_user(user_id)
        return {"name": user["name"]}

@app.put("/api/users/{user_id}/name")
async def update_user_name(user_id: str, data: Dict, auth: Dict = Depends(verify_token)):
    new_name = data.get("new_name")
    if not new_name:
        raise HTTPException(status_code=400, detail="new_name is required")
    
    user = get_or_create_user(user_id)
    user["name"] = new_name
    return {"status": "updated"}

@app.get("/api/users/{user_id}/info")
async def get_user_info(user_id: str, info_type: str, auth: Dict = Depends(verify_token)):
    user = get_or_create_user(user_id)
    
    if info_type == "courses":
        return user.get("courses", [])
    elif info_type == "tests":
        return user.get("tests", [])
    elif info_type == "scores":
        return user.get("scores", [])
    else:
        raise HTTPException(status_code=400, detail="Invalid info_type")

@app.get("/api/course")
async def get_all_courses(auth: Dict = Depends(verify_token)):
    if not mock_db["courses"]:
        mock_db["courses"] = {
            "1": {
                "id": "1",
                "name": "Алгоритмизация и основы программирования",
                "description": "Введение в программирование на C++ и GO",
                "instructor_id": "teacher_1"
            },
            "2": {
                "id": "2", 
                "name": "Веб-разработка",
                "description": "Создание веб-приложений",
                "instructor_id": "teacher_2"
            },
            "3": {
                "id": "3",
                "name": "Базы данных",
                "description": "SQL и NoSQL базы данных",
                "instructor_id": "teacher_3"
            }
        }
    
    courses = []
    for course_id, course_data in mock_db["courses"].items():
        courses.append({
            "id": course_data["id"],
            "name": course_data["name"],
            "description": course_data["description"]
        })
    return courses

@app.get("/api/course/{course_id}/info")
async def get_course_info(course_id: str, auth: Dict = Depends(verify_token)):
    if course_id in mock_db["courses"]:
        return mock_db["courses"][course_id]
    else:
        raise HTTPException(status_code=404, detail="Course not found")

@app.get("/api/tests")
async def get_all_tests(auth: Dict = Depends(verify_token)):
    if not mock_db["tests"]:
        mock_db["tests"] = {
            "1": {
                "id": "1",
                "name": "Тест по C++",
                "course_id": "1",
                "questions": ["1", "2", "3"]
            },
            "2": {
                "id": "2",
                "name": "Тест по Go",
                "course_id": "2", 
                "questions": ["4", "5"]
            },
            "3": {
                "id": "3",
                "name": "Экзаменационный тест",
                "course_id": "3", 
                "questions": ["6", "7", "8", "9", "10"]
            }
        }
    
    tests = []
    for test_id, test_data in mock_db["tests"].items():
        tests.append({
            "id": test_data["id"],
            "name": test_data["name"],
            "course_id": test_data["course_id"]
        })
    return tests

@app.get("/api/tests/{test_id}")
async def get_test_info(test_id: str, auth: Dict = Depends(verify_token)):
    if test_id in mock_db["tests"]:
        return mock_db["tests"][test_id]
    else:
        raise HTTPException(status_code=404, detail="Test not found")

@app.get("/api/questions")
async def get_all_questions(auth: Dict = Depends(verify_token)):
    if not mock_db["questions"]:
        mock_db["questions"] = {
            "1": {
                "id": "1",
                "name": "Типы данных в C++",
                "version": 1,
                "author_id": "teacher_1",
                "text": "Какой из перечисленных типов данных есть в C++?",
                "options": {
                    "0": "int",
                    "1": "list", 
                    "2": "dict",
                    "3": "str"
                },
                "correct_option": 0
            },
            "2": {
                "id": "2",
                "name": "Функции в C++",
                "version": 1,
                "author_id": "teacher_1",
                "text": "Что возвращает функция, если в ней нет оператора return?",
                "options": {
                    "0": "Пустую строку",
                    "1": "0",
                    "2": "None",
                    "3": "Ошибку"
                },
                "correct_option": 2
            }
        }
    
    questions = []
    for q_id, q_data in mock_db["questions"].items():
        questions.append({
            "id": q_data["id"],
            "name": q_data["name"],
            "version": q_data["version"],
            "author_id": q_data["author_id"]
        })
    return questions

@app.get("/notifications")
async def get_notifications(auth: Dict = Depends(verify_token)):
    user_id = auth.get("user_id", "unknown")
    
    notifications = []
    if random.random() > 0.8:
        notifications.append(f"Новый тест доступен в курсе 'Алгоритмизация и основы программирования'")
    
    return notifications

@app.delete("/notifications")
async def delete_notifications(auth: Dict = Depends(verify_token)):
    return {"status": "deleted"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "mock_main_module"}

if __name__ == "__main__":
    print("Mock Main Module запущен на http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)