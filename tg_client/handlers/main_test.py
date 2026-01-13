from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from utils.token_utils import make_authorized_request
from utils.redis_utils import get_user_state
from utils.main_api_client import main_api_client
import jwt

router = Router()

@router.message(Command("tests"))
async def tests_command(message: Message):
    chat_id = message.chat.id
    tests, error = await make_authorized_request(chat_id, "GET", "/api/tests")
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    if len(tests) > 0:
        response_text = "Доступные тесты:\n\n"
        for i in range(len(tests)):
            name = tests[i].get('name')
            test_id = tests[i].get('id')
            response_text += f"{i}. {name} (ID: {test_id})\n"
        await message.answer(response_text)
    else:
        await message.answer("Нет доступных тестов.")

@router.message(Command("courses"))
async def courses_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    try:
        response = await main_api_client.make_request(
            "GET", 
            "/api/course", 
            user_state.get('access_token')
        )
        
        if response.status_code == 200:
            courses = response.json()
            if courses and len(courses) > 0:
                response_text = "Доступные курсы:\n\n"
                for i, course in enumerate(courses):
                    name = course.get('name', 'Без названия')
                    course_id = course.get('id', '?')
                    description = course.get('description', '')
                    response_text += f"{i+1}. {name} (ID: {course_id})\n"
                    if description:
                        response_text += f"   {description}\n"
                await message.answer(response_text)
            else:
                await message.answer("Нет доступных курсов.")
        else:
            await message.answer(f"Ошибка получения курсов: {response.status_code}")
            
    except Exception as e:
        await message.answer(f"Ошибка подключения: {e}")

@router.message(Command("profile"))
async def profile_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    user_id = user_state.get('user_id')
    
    try:
        response = await main_api_client.make_request(
            "GET", 
            f"/api/users/{user_id}/name", 
            user_state.get('access_token')
        )
        
        if response.status_code == 200:
            name = response.json().get('name', 'Не указано')
            await message.answer(f"Ваш профиль\nID: {user_id}\nИмя: {name}")
        elif response.status_code == 404:
            await message.answer(
                f"Ваш профиль\nID: {user_id}\n"
                f"Имя: Не указано (пользователь не найден в главном модуле)\n\n"
            )
        else:
            await message.answer(f"Ваш профиль\nID: {user_id}\nОшибка: {response.status_code}")
            
    except Exception as e:
        await message.answer(f"Ваш профиль\nID: {user_id}\nОшибка подключения: {e}")

@router.message(Command("mycourses"))
async def my_courses_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    user_id = user_state.get('user_id')
    
    if not user_id:
        await message.answer("Не удалось получить ваш ID")
        return
    
    result, error = await make_authorized_request(chat_id, "GET", f"/api/users/{user_id}/info", 
                                                 params={"info_type": "courses"})
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if len(result) > 0:
        response_text = "Ваши курсы:\n\n"
        for i in range(len(result)):
            course_id = result[i].get('id', '?')
            name = result[i].get('name', 'Без названия')
            response_text += f"{i}. {name} (ID: {course_id})\n"
        await message.answer(response_text)
    else:
        await message.answer("У вас нет курсов.")

@router.message(Command("mytests"))
async def my_tests_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    user_id = user_state.get('user_id')
    
    if not user_id:
        await message.answer("Не удалось получить ваш ID")
        return
    
    result, error = await make_authorized_request(chat_id, "GET", f"/api/users/{user_id}/info", 
                                                 params={"info_type": "tests"})
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if len(result) > 0:
        response_text = "Ваши тесты:\n\n"
        for i in range(len(result)):
            test_id = result[i].get('id', '?')
            name = result[i].get('name', 'Без названия')
            response_text += f"{i}. {name} (ID: {test_id})\n"
        await message.answer(response_text)
    else:
        await message.answer("У вас нет доступных тестов.")

@router.message(Command("myscores"))
async def my_scores_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    user_id = user_state.get('user_id')
    
    if not user_id:
        await message.answer("Не удалось получить ваш ID")
        return
    
    result, error = await make_authorized_request(chat_id, "GET", f"/api/users/{user_id}/info", 
                                                 params={"info_type": "scores"})
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if len(result) > 0:
        response_text = "Ваши оценки:\n\n"
        for i in range(len(result)):
            test_name = result[i].get('test_name', 'Неизвестный тест')
            score_value = result[i].get('score', 0)
            max_score = result[i].get('max_score', 100)
            response_text += f"{i}. {test_name}: {score_value}/{max_score}\n"
        await message.answer(response_text)
    else:
        await message.answer("У вас нет оценок.")

@router.message(Command("course"))
async def course_info_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    
    if not command or not command.args:
        await message.answer("Использование: /course <ID курса>")
        return
    
    course_id = command.args.strip()
    
    result, error = await make_authorized_request(chat_id, "GET", f"/api/course/{course_id}/info")
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    name = result.get('name', 'Без названия')
    description = result.get('description', 'Нет описания')
    instructor_id = result.get('instructor_id', 'Неизвестно')
    
    await message.answer(
        f"Информация о курсе\n\nID: {course_id}\nНазвание: {name}\nОписание: {description}\nID Преподавателя: {instructor_id}"
    )

@router.message(Command("test"))
async def test_info_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    
    if not command or not command.args:
        await message.answer("Использование: /test <ID теста>")
        return
    
    test_id = command.args.strip()
    
    result, error = await make_authorized_request(chat_id, "GET", f"/api/tests/{test_id}")
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    name = result.get('name', 'Без названия')
    course_id = result.get('course_id', 'Неизвестно')
    question_count = len(result.get('questions', []))
    
    await message.answer(
        f"Информация о тесте\n\nID: {test_id}\nНазвание: {name}\nID Курса: {course_id}\nВопросов: {question_count}"
    )

@router.message(Command("questions"))
async def questions_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    try:
        response = await main_api_client.make_request(
            "GET", 
            "/api/questions", 
            user_state.get('access_token')
        )
        
        if response.status_code == 200:
            questions = response.json()
            if questions and len(questions) > 0:
                response_text = "Доступные вопросы:\n\n"
                for i, question in enumerate(questions):
                    name = question.get('name', 'Без названия')
                    question_id = question.get('id', '?')
                    version = question.get('version', 1)
                    response_text += f"{i}. {name} (ID: {question_id}, версия: {version})\n"
                await message.answer(response_text)
            else:
                await message.answer("Нет доступных вопросов.")
        else:
            await message.answer(f"Ошибка получения вопросов: {response.status_code}")
            
    except Exception as e:
        await message.answer(f"Ошибка подключения: {e}")