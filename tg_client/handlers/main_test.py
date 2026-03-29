from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from utils.token_utils import make_authorized_request
from utils.redis_utils import get_user_state
from utils.main_api_client import main_api_client

router = Router()

@router.message(Command("courses"))
async def courses_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    result, error = await main_api_client.make_request("GET", "/api/course", chat_id)
    
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if isinstance(result, list) and len(result) > 0:
        response_text = "Доступные курсы:\n\n"
        for i, course in enumerate(result):
            name = course.get('name', 'Без названия')
            course_id = course.get('id', '?')
            description = course.get('description', '')
            response_text += f"{i+1}. {name} (ID: {course_id})\n"
            if description:
                response_text += f"   {description}\n\n"
        await message.answer(response_text)
    else:
        await message.answer("Нет доступных курсов.")

@router.message(Command("profile"))
async def profile_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    result, error = await make_authorized_request(chat_id, "GET", "/api/user_id")
    
    if error:
        user_id = user_state.get('user_id')
        if not user_id:
            await message.answer("Не удалось получить ваш ID")
            return
    else:
        user_id = result.get('user_id') if isinstance(result, dict) else str(result)
    
    name_result, name_error = await make_authorized_request(chat_id, "GET", f"/api/users/{user_id}/name")
    
    response_text = f"Ваш профиль\nID: {user_id}\n"
    
    if name_error:
        if "404" in name_error:
            response_text += "Имя: Не указано\nСменить имя: /name"
            
        else:
            response_text += f"Имя: Неизвестно (ошибка: {name_error})\nСменить имя: /set_name"
    else:
        if isinstance(name_result, dict):
            name = name_result.get('name', 'Не указано')
        else:
            name = str(name_result) if name_result else 'Не указано'
        response_text += f"Имя: {name}"
    
    await message.answer(response_text)

@router.message(Command("id"))
async def id_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    result, error = await make_authorized_request(chat_id, "GET", "/api/user_id")
    
    if error:
        user_id = user_state.get('user_id')
        if user_id:
            await message.answer(f"Ваш ID: {user_id}\n(из токена, эндпоинт /api/user_id недоступен)")
        else:
            await message.answer(f"Не удалось получить ID. Ошибка: {error}")
    else:
        if isinstance(result, dict):
            user_id = result.get('user_id')
            await message.answer(f"Ваш ID: {user_id}")
        else:
            await message.answer(f"Ответ: {result}")

@router.message(Command("mycourses"))
async def my_courses_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    id_result, id_error = await make_authorized_request(chat_id, "GET", "/api/user_id")
    
    if id_error:
        await message.answer(f"Не удалось получить ваш ID: {id_error}")
        return    
    
    if isinstance(id_result, dict):
        numeric_id = id_result.get('user_id')
    else:
        numeric_id = str(id_result) if id_result else None
    
    if not numeric_id:
        await message.answer("Не удалось получить ваш numeric_id")
        return
    
    result, error = await make_authorized_request(
        chat_id, "GET", f"/api/users/{numeric_id}/info",
        params={"info_type": "courses"}
    )
    
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if isinstance(result, list) and len(result) > 0:
        response_text = "Ваши курсы:\n\n"
        for i, course in enumerate(result):
            if isinstance(course, dict):
                course_id = course.get('id', '?')
                name = course.get('name', 'Без названия')
                response_text += f"{i+1}. {name} (ID: {course_id})\n\n"
            else:
                response_text += f"{i+1}. {str(course)}\n\n"
        await message.answer(response_text)
    else:
        await message.answer("У вас нет курсов.")

@router.message(Command("course"), ~F.text.contains(" "))
async def course_no_args(message: Message):
    await message.answer("Использование: /course [ID курса]")

@router.message(Command("course"))
async def course_info_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id    
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

@router.message(Command("test"), ~F.text.contains(" "))
async def test_no_args(message: Message):
    await message.answer("Использование: /test [ID теста]")

@router.message(Command("test"))
async def test_info_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id    
    if not command or not command.args:
        await message.answer("Использование: /test [test_id]")
        return
    
    test_id = command.args.strip()
    id_result, id_error = await make_authorized_request(chat_id, "GET", "/api/user_id")
    
    if id_error:
        await message.answer(f"Не удалось получить ваш ID: {id_error}")
        return    
    
    if isinstance(id_result, dict):
        numeric_id = id_result.get('user_id')
    else:
        numeric_id = str(id_result) if id_result else None
    
    if not numeric_id:
        await message.answer("Не удалось получить ваш numeric_id")
        return
    
    result, error = await make_authorized_request(
        chat_id, "GET", f"/api/users/{numeric_id}/info",
        params={"info_type": "courses"}
    )
    
    if error:
        await message.answer(f"Ошибка получения курсов: {error}")
        return
    
    if not isinstance(result, list):
        await message.answer(f"Тест {test_id} не найден в ваших курсах")
        return
    
    for course in result:
        if isinstance(course, dict):
            course_id = course.get('id')
            if course_id:
                tests_result, tests_error = await make_authorized_request(
                    chat_id, "GET", f"/api/course/{course_id}/tests"
                )
                
                if not tests_error and isinstance(tests_result, list):
                    for test in tests_result:
                        if str(test.get('id')) == test_id:
                            test_name = test.get('name', 'Без названия')
                            active = test.get('active', False)
                            status = "активен" if active else "не активен"
                            
                            await message.answer(
                                f"Информация о тесте\n\nID: {test_id}\n"
                                f"Название: {test_name}\nID Курса: {course_id}\n"
                                f"Статус: {status}"
                            )
                            return
    
    await message.answer(f"Тест {test_id} не найден в ваших курсах")