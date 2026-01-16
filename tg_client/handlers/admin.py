from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from typing import Optional
from utils.redis_utils import get_user_state
from utils.token_utils import make_authorized_request
import jwt
import json

router = Router()

def check_permission(user_state: dict, required_permission: str) -> bool:
    access_token = user_state.get('access_token')
    if not access_token:
        return False
    
    try:
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        permissions = decoded.get('permissions', [])
        roles = decoded.get('roles', [])
        
        if required_permission in permissions:
            return True
        
        if 'admin' in roles:
            return True
            
        if 'teacher' in roles and required_permission.startswith('course.'):
            return True
            
    except Exception:
        return False
    
    return False

@router.message(Command("users"))
async def list_users_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not check_permission(user_state, 'user:list:read'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "GET", "/api/users")
    
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if not result:
        await message.answer("Нет пользователей")
        return
    
    response = "Список пользователей:\n\n"
    for i, user in enumerate(result, 1):
        response += f"{i}. {user.get('name', 'Без имени')} (ID: {user.get('id', '?')})\n"
    
    await message.answer(response)

@router.message(Command("user_info"))
async def user_info_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /user_info [user_id] [info_type]\ninfo_type: courses, scores, tests")
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer("Использование: /user_info [user_id] [info_type]\ninfo_type: courses, scores, tests")
        return
    
    user_id, info_type = args[0], args[1]
    
    if info_type not in ['courses', 'scores', 'tests']:
        await message.answer("Неверный info_type. Используйте: courses, scores, tests")
        return
    
    if not check_permission(user_state, 'user:data:read'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "GET", f"/api/users/{user_id}/info",
                                                 params={"info_type": info_type})
    
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if not result:
        await message.answer(f"Нет информации для пользователя {user_id}")
        return
    
    response = f"Информация о пользователе {user_id} ({info_type}):\n\n"

    if isinstance(result, list):
        if info_type == 'courses':
            for i, course in enumerate(result, 1):
                if isinstance(course, dict):
                    response += f"{i}. {course.get('name', 'Без названия')} (ID: {course.get('id', '?')})\n"
                else:
                    response += f"{i}. {str(course)}\n"
        elif info_type == 'scores':
            for i, score in enumerate(result, 1):
                if isinstance(score, dict):
                    response += f"{i}. Тест: {score.get('test_name', 'Неизвестно')} - {score.get('score', 0)} баллов\n"
                else:
                    response += f"{i}. {str(score)}\n"
        elif info_type == 'tests':
            for i, test in enumerate(result, 1):
                if isinstance(test, dict):
                    response += f"{i}. {test.get('name', 'Без названия')} (ID: {test.get('id', '?')})\n"
                else:
                    response += f"{i}. {str(test)}\n"
    else:
        response += str(result)
    
    await message.answer(response)

@router.message(Command("set_name"))
async def set_user_name_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /set_name [user_id] [новое_имя]")
        return
    
    args = command.args.strip().split(maxsplit=1)
    if len(args) != 2:
        await message.answer("Использование: /set_name [user_id] [новое_имя]")
        return
    
    user_id, new_name = args[0], args[1]
    
    if not check_permission(user_state, 'user:fullName:write'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "PUT", f"/api/users/{user_id}/name",
                                                 data={"new_name": new_name})
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Имя пользователя {user_id} изменено")

@router.message(Command("user_roles"))
async def user_roles_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование:\n/user_roles [user_id] - просмотреть роли\n/user_roles [user_id] set [role1,role2] - установить роли")
        return
    
    args = command.args.strip().split()
    
    if len(args) == 1:
        user_id = args[0]
        
        if not check_permission(user_state, 'user:roles:read'):
            await message.answer("Недостаточно прав")
            return
        
        result, error = await make_authorized_request(chat_id, "GET", f"/api/users/{user_id}/roles")
        
        if error:
            await message.answer(f"Ошибка: {error}")
        else:
            roles = result if isinstance(result, list) else []
            await message.answer(f"Роли пользователя {user_id}:\n{', '.join(roles) if roles else 'нет ролей'}")
    
    elif len(args) >= 3 and args[1] == 'set':
        user_id = args[0]
        roles_str = ' '.join(args[2:])
        
        try:
            roles = json.loads(roles_str)
        except:
            roles = [role.strip() for role in roles_str.split(',')]
        
        if not check_permission(user_state, 'user:roles:write'):
            await message.answer("Недостаточно прав")
            return
        
        result, error = await make_authorized_request(chat_id, "POST", f"/api/users/{user_id}/roles",
                                                     data={"roles": roles})
        
        if error:
            await message.answer(f"Ошибка: {error}")
        else:
            await message.answer(f"Роли пользователя {user_id} обновлены")
    
    else:
        await message.answer("Неверный формат команды")

@router.message(Command("block_user"))
async def block_user_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /block_user [user_id] [true/false]")
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer("Использование: /block_user [user_id] [true/false]")
        return
    
    user_id, block_flag = args[0], args[1].lower()
    
    if block_flag not in ['true', 'false']:
        await message.answer("Второй аргумент должен быть 'true' или 'false'")
        return
    
    blocked = block_flag == 'true'
    
    if not check_permission(user_state, 'user:block:write'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "POST", f"/api/users/{user_id}/blocked",
                                                 data={"blocked": blocked})
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        status = "заблокирован" if blocked else "разблокирован"
        await message.answer(f"Пользователь {user_id} {status}")

@router.message(Command("create_course"))
async def create_course_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /create_course [название] [описание] [instructor_id]")
        return
    
    args = command.args.strip().split(maxsplit=2)
    if len(args) != 3:
        await message.answer("Использование: /create_course [название] [описание] [instructor_id]")
        return
    
    name, description, instructor_id = args[0], args[1], args[2]
    
    if not check_permission(user_state, 'course:add'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "POST", "/api/course",
                                                 data={
                                                     "name": name,
                                                     "description": description,
                                                     "instructor_id": instructor_id
                                                 })
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        course_id = result.get('course_id') if result else 'неизвестен'
        await message.answer(f"Курс создан! ID: {course_id}")

@router.message(Command("update_course"))
async def update_course_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /update_course [course_id] [новое_название] [новое_описание]")
        return
    
    args = command.args.strip().split(maxsplit=2)
    if len(args) != 3:
        await message.answer("Использование: /update_course [course_id] [новое_название] [новое_описание]")
        return
    
    course_id, name, description = args[0], args[1], args[2]
    
    if not check_permission(user_state, 'course:info:write'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "PUT", f"/api/course/{course_id}/info",
                                                 data={"name": name, "description": description})
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Информация о курсе {course_id} обновлена")

@router.message(Command("delete_course"))
async def delete_course_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /delete_course [course_id]")
        return
    
    course_id = command.args.strip()
    
    if not check_permission(user_state, 'course:del'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "DELETE", f"/api/course/{course_id}")
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Курс {course_id} удален")

@router.message(Command("course_students"))
async def course_students_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /course_students [course_id]")
        return
    
    course_id = command.args.strip()
    
    if not check_permission(user_state, 'course:userList'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "GET", f"/api/course/{course_id}/students")
    
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if not result:
        await message.answer(f"На курсе {course_id} нет студентов")
        return
    
    response = f"Студенты курса {course_id}:\n\n"
    for i, student_id in enumerate(result, 1):
        response += f"{i}. ID: {student_id}\n"
    
    await message.answer(response)

@router.message(Command("add_to_course"))
async def add_to_course_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /add_to_course [course_id] [user_id]")
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer("Использование: /add_to_course [course_id] [user_id]")
        return
    
    course_id, user_id = args[0], args[1]
    
    if not check_permission(user_state, 'course:user:add'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "POST", f"/api/course/{course_id}/students",
                                                 data={"user_id": user_id})
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Пользователь {user_id} добавлен на курс {course_id}")

@router.message(Command("remove_from_course"))
async def remove_from_course_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /remove_from_course [course_id] [user_id]")
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer("Использование: /remove_from_course [course_id] [user_id]")
        return
    
    course_id, user_id = args[0], args[1]
    
    if not check_permission(user_state, 'course:user:del'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "DELETE", f"/api/course/{course_id}/students",
                                                 data={"user_id": user_id})
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Пользователь {user_id} удален с курса {course_id}")

@router.message(Command("add_test"))
async def add_test_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /add_test [course_id] [название_теста]")
        return
    
    args = command.args.strip().split(maxsplit=1)
    if len(args) != 2:
        await message.answer("Использование: /add_test [course_id] [название_теста]")
        return
    
    course_id, test_name = args[0], args[1]
    
    if not check_permission(user_state, 'course:test:add'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "POST", f"/api/course/{course_id}/tests",
                                                 data={"test_name": test_name})
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        test_id = result.get('test_id') if result else 'неизвестен'
        await message.answer(f"Тест добавлен. ID: {test_id}")

@router.message(Command("remove_test"))
async def remove_test_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /remove_test [course_id] [test_id]")
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer("Использование: /remove_test [course_id] [test_id]")
        return
    
    course_id, test_id = args[0], args[1]
    
    if not check_permission(user_state, 'course:test:del'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "DELETE", f"/api/course/{course_id}/tests/{test_id}")
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Тест {test_id} удален")

@router.message(Command("set_test_active"))
async def set_test_active_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /set_test_active [course_id] [test_id] [true/false]")
        return
    
    args = command.args.strip().split()
    if len(args) != 3:
        await message.answer("Использование: /set_test_active [course_id] [test_id] [true/false]")
        return
    
    course_id, test_id, activity = args[0], args[1], args[2].lower()
    
    if activity not in ['true', 'false']:
        await message.answer("Третий аргумент должен быть 'true' или 'false'")
        return
    
    is_active = activity == 'true'
    
    if not check_permission(user_state, 'course:test:write'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "POST", f"/api/course/{course_id}/tests/{test_id}/active",
                                                 data={"activity": is_active})
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        status = "активирован" if is_active else "деактивирован"
        await message.answer(f"Тест {test_id} {status}")

@router.message(Command("test_results"))
async def test_results_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /test_results [test_id]")
        return
    
    test_id = command.args.strip()
    
    if not check_permission(user_state, 'test:answer:read'):
        await message.answer("Недостаточно прав")
        return
    
    scores_result, scores_error = await make_authorized_request(chat_id, "GET", f"/api/tests/{test_id}/scores")
    
    if scores_error:
        await message.answer(f"Ошибка: {scores_error}")
        return
    
    response = f"Результаты теста {test_id}:\n\n"
    
    if scores_result:
        for score_data in scores_result:
            user_id = score_data.get('user_id', 'неизвестен')
            score = score_data.get('score', 0)
            response += f"{user_id}: {score} баллов\n"
    else:
        response += "Нет результатов"
    
    await message.answer(response)

@router.message(Command("create_question"))
async def create_question_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /create_question [JSON с данными вопроса]")
        return
    
    try:
        question_data = json.loads(command.args)
        
        required_fields = ['name', 'text', 'options', 'correct_option']
        for field in required_fields:
            if field not in question_data:
                await message.answer(f"Отсутствует поле: {field}")
                return
        
        if not check_permission(user_state, 'quest:create'):
            await message.answer("Недостаточно прав")
            return
        
        result, error = await make_authorized_request(chat_id, "POST", "/api/questions",
                                                     data=question_data)
        
        if error:
            await message.answer(f"Ошибка: {error}")
        else:
            question_id = result.get('question_id') if result else 'неизвестен'
            await message.answer(f"Вопрос создан! ID: {question_id}")
            
    except json.JSONDecodeError:
        await message.answer("Неверный формат JSON")

@router.message(Command("add_to_test"))
async def add_to_test_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer("Использование: /add_to_test [test_id] [question_id]")
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer("Использование: /add_to_test [test_id] [question_id]")
        return
    
    test_id, question_id = args[0], args[1]
    
    if not check_permission(user_state, 'test:quest:add'):
        await message.answer("Недостаточно прав")
        return
    
    result, error = await make_authorized_request(chat_id, "POST", f"/api/tests/{test_id}/questions",
                                                 data={"question_id": question_id})
    
    if error:
        await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Вопрос {question_id} добавлен в тест {test_id}")

@router.message(Command("admin_help"))
async def admin_help_command(message: Message):
    help_text = """
Команды для учителей и администраторов:

Управление пользователями:
/users - список пользователей
/user_info [id] [type] - информация о пользователе
/set_name [id] [имя] - изменить имя
/user_roles [id] - показать роли
/user_roles [id] set [роли] - установить роли
/block_user [id] [true/false] - блокировка

Управление курсами:
/create_course [название] [описание] [instructor_id]
/update_course [id] [название] [описание]
/delete_course [id]
/course_students [id]
/add_to_course [course_id] [user_id]
/remove_from_course [course_id] [user_id]

Управление тестами:
/add_test [course_id] [название]
/remove_test [course_id] [test_id]
/set_test_active [course_id] [test_id] [true/false]
/test_results [test_id]

Управление вопросами:
/create_question [JSON]
/add_to_test [test_id] [question_id]
    """
    
    await message.answer(help_text)