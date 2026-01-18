from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from typing import Optional
from utils.redis_utils import get_user_state
from utils.token_utils import make_authorized_request
from utils.config import Config
import jwt
import httpx
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
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer("Использование:\n"
                           "/set_name [новое_имя] - сменить своё имя\n"
                           "/set_name [user_id] [новое_имя] - сменить имя другого пользователя")
        return
    
    args = command.args.strip().split(maxsplit=1)
    
    if len(args) == 1:
        new_name = args[0]
        id_result, id_error = await make_authorized_request(chat_id, "GET", "/api/user_id")
        
        if id_error:
            await message.answer(f"Не удалось получить ваш ID: {id_error}")
            return
        
        numeric_id = id_result.get('user_id') if isinstance(id_result, dict) else str(id_result)
        
        result, error = await make_authorized_request(
            chat_id, "PUT", f"/api/users/{numeric_id}/name",
            data={"new_name": new_name}
        )
        
        if error:
            await message.answer(f"Ошибка: {error}")
        else:
            await message.answer(f"Ваше имя изменено на '{new_name}'")
    
    elif len(args) == 2:
        target_user_id, new_name = args[0], args[1]
        
        id_result, id_error = await make_authorized_request(chat_id, "GET", "/api/user_id")
        result, error = await make_authorized_request(
            chat_id, "PUT", f"/api/users/{target_user_id}/name",
            data={"new_name": new_name}
        )
        
        if error:
            await message.answer(f"Ошибка: {error}")
        else:
            await message.answer(f"Имя пользователя {target_user_id} изменено на '{new_name}'")


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
            await message.answer("Недостаточно прав для просмотра ролей")
            return
        
        result, error = await make_authorized_request(
            chat_id, "GET", f"/api/users/{user_id}/roles"
        )
        
        if error:
            await message.answer(f"Ошибка: {error}")
            return
        
        roles = []
        
        if isinstance(result, dict):
            if 'roles' in result:
                roles = result['roles']
            elif 'role' in result:
                roles = [result['role']]
        elif isinstance(result, list):
            roles = result
        
        await message.answer(
            f"Роли пользователя {user_id}:\n" + 
            (', '.join([str(r) for r in roles]) if roles else 'нет ролей')
        )
    
    elif len(args) >= 3 and args[1] == 'set':
        user_id = args[0]
        roles_str = ' '.join(args[2:])
        
        try:
            import json
            if roles_str.startswith('[') and roles_str.endswith(']'):
                roles = json.loads(roles_str)
            elif ',' in roles_str:
                roles = [role.strip() for role in roles_str.split(',')]
            else:
                roles = [roles_str.strip()]
        except json.JSONDecodeError:
            roles = [role.strip() for role in roles_str.split(',')]
        except Exception as e:
            await message.answer(f"Ошибка парсинга ролей: {e}")
            return
        
        if not check_permission(user_state, 'user:roles:write'):
            await message.answer("Недостаточно прав для изменения ролей")
            return
        
        result_id, error_id = await make_authorized_request(
            chat_id, "GET", f"/api/{user_id}/auth_id"
        )
        
        if error_id:
            await message.answer(f"Ошибка получения auth_id: {error_id}")
            return
        
        auth_id = None
        if isinstance(result_id, dict):
            auth_id = result_id.get('auth_id')
        elif result_id:
            auth_id = str(result_id)
        
        if not auth_id:
            await message.answer(f"Не удалось получить auth_id для пользователя {user_id}")
            return
        
        from utils.config import Config
        auth_base_url = Config.AUTH_SERVER_URL.rstrip('/')
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": f"Bearer {user_state.get('access_token')}",
                    "Content-Type": "application/json"
                }
                
                response = await client.post(
                    f"{auth_base_url}/users/{auth_id}/roles",
                    headers=headers,
                    json={"roles": roles}
                )
                
                if response.status_code in [200, 201, 204]:
                    await message.answer(f"Роли пользователя {user_id} обновлены")
                else:
                    error_msg = f"Ошибка от сервера авторизации: {response.status_code}"
                    if response.text:
                        error_msg += f" - {response.text[:200]}"
                    
                    if response.status_code == 500:
                        await message.answer(
                            f"{error_msg}\n\n"
                            "Возможные причины:\n"
                            "1. Неверный формат ролей (должны быть: ['student', 'teacher', 'admin'])\n"
                            "2. Попытка удалить все роли у пользователя\n"
                            "3. Проблема на сервере авторизации"
                        )
                    else:
                        await message.answer(error_msg)
                        
        except Exception as e:
            await message.answer(f"Ошибка запроса к серверу авторизации: {e}")
    
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
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer(
            "Создание курса\n\n"
            "Использование:\n"
            '/create_course "Название курса" "Описание курса" instructor_id'
        )
        return
    
    args = command.args.strip()    
    
    try:
        course_data = json.loads(args)       
        
        required_fields = ['name', 'description', 'instructor_id']
        missing_fields = [f for f in required_fields if f not in course_data]
        
        if missing_fields:
            await message.answer(f"В JSON отсутствуют поля: {', '.join(missing_fields)}")
            return            
        
        try:
            instructor_id = int(course_data['instructor_id'])
        except ValueError:
            await message.answer("instructor_id должен быть числом")
            return
        
    except json.JSONDecodeError:
        
        import shlex
        try:            
            parsed_args = shlex.split(args)
            
            if len(parsed_args) < 3:
                await message.answer(
                    "Недостаточно аргументов. Нужно 3 аргумента:\n"
                    '1. "Название курса"\n'
                    '2. "Описание курса"\n'
                    '3. instructor_id (число)\n\n'
                    'Пример:\n'
                    '/create_course "Python" "Курс по программированию" 1'
                )
                return            
            
            try:
                instructor_id = int(parsed_args[-1])
            except ValueError:
                await message.answer(f"instructor_id должен быть числом, получено: {parsed_args[-1]}")
                return
            
            
            if len(parsed_args) == 3:
                
                name, description, _ = parsed_args
            else:
                
                name = parsed_args[0]
                description = ' '.join(parsed_args[1:-1])
            
            course_data = {
                "name": name.strip('"\' '),
                "description": description.strip('"\' '),
                "instructor_id": instructor_id
            }
            
        except ValueError as e:
            await message.answer(f"Ошибка парсинга аргументов: {e}\n\n"
                               "Используйте кавычки для названия и описания!")
            return    
    
    result, error = await make_authorized_request(
        chat_id, "POST", "/api/course",
        data=course_data
    )
    
    if error:
        await message.answer(f"Ошибка создания курса: {error}")
    else:
        course_id = result.get('course_id') if isinstance(result, dict) else result
        await message.answer(
            "Курс создан!\n"
            f"ID курса: {course_id}\n"
            f"Посмотреть курс: /course {course_id}"
        )
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
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer("Использование: /add_to_course [course_id] [user_id]")
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer("Использование: /add_to_course [course_id] [user_id]")
        return
    
    course_id, target_user_id = args[0], args[1]
    
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
    
    checking_self = str(target_user_id) == str(numeric_id)
    
    course_info, course_error = await make_authorized_request(
        chat_id, "GET", f"/api/course/{course_id}/info"
    )
    
    if course_error:
        await message.answer(f"Курс {course_id} не найден: {course_error}")
        return
    
    course_name = course_info.get('name', 'Без названия')
    instructor_id = course_info.get('instructor_id')
    
    if checking_self:
        if instructor_id and str(instructor_id) == str(numeric_id):
            await message.answer("Вы преподаватель этого курса, не можете записаться как студент.")
            return
        
        students_result, students_error = await make_authorized_request(
            chat_id, "GET", f"/api/course/{course_id}/students"
        )
        
        if not students_error and isinstance(students_result, list):
            if str(numeric_id) in [str(sid) for sid in students_result]:
                await message.answer(f"Вы уже записаны на курс '{course_name}'")
                return
    
    try:
        user_id_int = int(target_user_id)
    except ValueError:
        user_id_int = target_user_id
    
    result, error = await make_authorized_request(
        chat_id, "POST", f"/api/course/{course_id}/students",
        data={"user_id": user_id_int}
    )
    
    if error:
        if "500" in error:
            await message.answer(
                f"Ошибка сервера при добавлении пользователя {target_user_id} на курс.\n\n"
                "Возможные причины:\n"
                "1. Курс не существует\n"
                "2. Пользователь уже записан на курс\n"
                "3. Пользователь не существует\n"
                "4. Проблема на сервере"
            )
        else:
            await message.answer(f"Ошибка: {error}")
    else:
        pronoun = "Вы" if checking_self else f"Пользователь {target_user_id}"
        await message.answer(f"{pronoun} добавлены на курс '{course_name}' (ID: {course_id})")

@router.message(Command("remove_from_course"))
async def remove_from_course_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    if not command or not command.args:
        await message.answer("Использование: /remove_from_course [course_id] [user_id]")
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer("Использование: /remove_from_course [course_id] [user_id]")
        return
    
    course_id, target_user_id = args[0], args[1]    
    
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
        chat_id, "DELETE", f"/api/course/{course_id}/students",
        data={"user_id": int(target_user_id)}
    )
    
    if error:
        if "500" in error:
            await message.answer(
                "Ошибка сервера при удалении с курса.\n\n"
                "Возможные причины:\n"
                "1. Курс не существует\n"
                "2. Пользователь не записан на курс\n"
                "3. Проблема на сервере"
            )
        else:
            await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Пользователь {target_user_id} удален с курса {course_id}")

@router.message(Command("add_test"))
async def add_test_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer(
            "Использование: /add_test [course_id] [название_теста]"
        )
        return
    
    args = command.args.strip()   
    try:        
        data = json.loads(args)
        await message.answer(
            "Для команды /add_test используйте формат с аргументами:\n"
            "/add_test [course_id] [название_теста]"
        )
        return
    except json.JSONDecodeError:        
        pass
    
    
    args_list = args.split(maxsplit=1)
    if len(args_list) != 2:
        await message.answer(
            "Неверный формат. Используйте:\n"
            "/add_test [course_id] [название_теста]"
        )
        return
    
    course_id_str, test_name = args_list[0], args_list[1].strip('"\' ')
    if not course_id_str.isdigit():
        await message.answer(f"course_id должен быть числом")
        return
    
    course_id = int(course_id_str)
    course_result, course_error = await make_authorized_request(
        chat_id, "GET", f"/api/course/{course_id}/info"
    )
    
    if course_error:        
        course_result2, course_error2 = await make_authorized_request(
            chat_id, "GET", f"/api/course/{course_id}"
        )        
        if course_error2:
            await message.answer(f"Курс {course_id} не найден. Ошибка: {course_error}")
            return    
    
    result, error = await make_authorized_request(
        chat_id, "POST", f"/api/course/{course_id}/tests",
        data={"test_name": test_name}
    )
    
    await message.answer(f"Тест '{test_name}' создан в курсе {course_id}!\nПроверьте тесты: /tests {course_id}")

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
    
    
    try:
        result, error = await make_authorized_request(
            chat_id, "POST", f"/api/tests/{test_id}/questions",
            data={"question_id": int(question_id) if question_id.isdigit() else question_id}
        )
        
        if error:
            if "500" in error:
                await message.answer(
                    "Ошибка сервера при добавлении вопроса в тест.\n\n"
                    "Возможные причины:\n"
                    "1. Тест не существует\n"
                    "2. Вопрос не существует\n"
                    "3. Тест уже имеет попытки прохождения (нельзя менять вопросы)\n"
                    "4. Вопрос уже добавлен в тест\n"
                    "5. У вас нет прав на изменение этого теста\n\n"
                    "Проверьте:\n"
                    f"- Существует ли тест: /test {test_id}\n"
                    f"- Существует ли вопрос: /question_info {question_id} 1\n"
                    f"- Ваши права: /my_permissions"
                )
            else:
                await message.answer(f"Ошибка: {error}")
        else:
            await message.answer(f"Вопрос {question_id} добавлен в тест {test_id}")
            
    except Exception as e:
        await message.answer(f"Исключение: {e}")


@router.message(Command("tests"))
async def view_tests_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer("Использование: /tests [course_id]")
        return
    
    course_id = command.args.strip()
    
    result, error = await make_authorized_request(
        chat_id, "GET", f"/api/course/{course_id}/tests"
    )
    
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    
    if not result or (isinstance(result, list) and len(result) == 0):
        await message.answer(f"В курсе {course_id} нет тестов")
        return
    
    response = f"Тесты курса {course_id}:\n\n"
    
    for i, test in enumerate(result, 1):
        test_id = test.get('id', '?')
        test_name = test.get('name', 'Без названия')
        
        response += f"{i}. {test_name} (ID: {test_id})\n"
        
        if 'active' in test:
            status = "Активен" if test['active'] else "Неактивен"
            response += f"   Статус: {status}\n"
        
        response += "\n"
    
    await message.answer(response)

@router.message(Command("remove_test"))
async def remove_test_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer(
            "Использование: /remove_test [course_id] [test_id]"
        )
        return
    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer(
            "Неверный формат. Используйте:\n"
            "/remove_test [course_id] [test_id]"
        )
        return
    
    course_id, test_id = args[0], args[1]
 
    tests_result, tests_error = await make_authorized_request(
        chat_id, "GET", f"/api/course/{course_id}/tests"
    )
    
    if tests_error:
        await message.answer(f"Не удалось получить тесты курса: {tests_error}")
        return    
    
    test_exists = False
    test_name = None    
    if isinstance(tests_result, list):
        for test in tests_result:
            if str(test.get('id')) == test_id:
                test_exists = True
                test_name = test.get('name', 'Без названия')
                break
    
    if not test_exists:
        available_tests = ""
        if isinstance(tests_result, list) and tests_result:
            available_tests = "Доступные тесты:\n"
            for test in tests_result:
                test_id_avail = test.get('id', '?')
                test_name_avail = test.get('name', 'Без названия')
                available_tests += f"• {test_name_avail} (ID: {test_id_avail})\n"
        
        await message.answer(
            f"Тест {test_id} не найден в курсе {course_id}\n\n"
            f"{available_tests}"
        )
        return    
    
    result, error = await make_authorized_request(
        chat_id, "DELETE", f"/api/course/{course_id}/tests/{test_id}"
    )
    
    if error:
        await message.answer(f"Ошибка удаления теста '{test_name}': {error}")
    else:
        await message.answer(f"Тест '{test_name}' (ID: {test_id}) удален из курса {course_id}")

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

@router.message(Command("questions"))
async def list_questions_command(message: Message, command: CommandObject = None):    
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not check_permission(user_state, 'quest:list:read'):
        id_result, id_error = await make_authorized_request(chat_id, "GET", "/api/user_id")
        if id_error:
            await message.answer(f"Не удалось получить ваш ID: {id_error}")
            return
        
        our_id = id_result.get('user_id') if isinstance(id_result, dict) else id_result

        await message.answer(
            "ℹУ вас нет прав на просмотр всех вопросов.\n"
            "Вы можете просматривать только свои вопросы.\n\n"
            "Используйте /my_questions для просмотра своих вопросов."
        )
        return
    
    result, error = await make_authorized_request(chat_id, "GET", "/api/questions")
    
    if error:
        await message.answer(f"Ошибка получения вопросов: {error}")
        return
    
    if not result or (isinstance(result, list) and len(result) == 0):
        await message.answer("Нет вопросов")
        return
    
    response = "Список вопросов:\n\n"
    
    for i, question in enumerate(result, 1):
        question_id = question.get('id', '?')
        name = question.get('name', 'Без названия')
        version = question.get('version', 1)
        author_id = question.get('author_id', '?')
        
        response += f"{i}. {name}\n"
        response += f"   ID: {question_id}, Версия: {version}, Автор: {author_id}\n\n"
    
    await message.answer(response)

@router.message(Command("my_questions"))
async def my_questions_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    id_result, id_error = await make_authorized_request(chat_id, "GET", "/api/user_id")
    if id_error:
        await message.answer(f"Не удалось получить ваш ID: {id_error}")
        return
    
    our_id = id_result.get('user_id') if isinstance(id_result, dict) else id_result
    
    result, error = await make_authorized_request(chat_id, "GET", "/api/questions")
    
    if error:
        await message.answer(f"Ошибка получения вопросов: {error}")
        return
    
    if not result or (isinstance(result, list) and len(result) == 0):
        await message.answer("У вас нет вопросов")
        return
    
    my_questions = []
    for question in result:
        author_id = question.get('author_id')
        if author_id and str(author_id) == str(our_id):
            my_questions.append(question)
    
    if not my_questions:
        await message.answer("У вас нет созданных вопросов")
        return
    
    response = f"Ваши вопросы ({len(my_questions)}):\n\n"
    
    for i, question in enumerate(my_questions, 1):
        question_id = question.get('id', '?')
        name = question.get('name', 'Без названия')
        version = question.get('version', 1)
        
        response += f"{i}. {name}\n"
        response += f"   ID: {question_id}, Версия: {version}\n"
        response += f"   Просмотреть: /question_info {question_id}\n"
        response += f"   Обновить: /update_question {question_id} [JSON]\n"
        response += f"   Удалить: /delete_question {question_id}\n\n"
    
    await message.answer(response)

@router.message(Command("question_info"))
async def question_info_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer(
            "Использование: /question_info [question_id] [version]"
        )
        return
    
    args = command.args.strip().split()
    
    if len(args) == 2:
        question_id, version = args[0], args[1]
    else:
        await message.answer("Неверный формат. Используйте: /question_info [id] [version]")
        return
    
    endpoint = f"/api/questions/{question_id}"
    params = {"version": version} if version else None
    
    result, error = await make_authorized_request(
        chat_id, "GET", endpoint, params=params
    )
    
    if error:
        if "404" in error:
            await message.answer(f"Вопрос {question_id} не найден")
        elif "403" in error:
            await message.answer(f"Нет прав для просмотра этого вопроса")
        else:
            await message.answer(f"Ошибка: {error}")
        return
    
    name = result.get('name', 'Без названия')
    text = result.get('text', 'Нет текста')
    options = result.get('options', [])
    correct_option = result.get('correct_option')
    question_version = result.get('version', 1)
    
    response = f"Вопрос ID: {question_id}\n"
    response += f"Название: {name}\n"
    response += f"Версия: {question_version}\n\n"
    response += f"Текст вопроса:\n{text}\n\n"
    
    if options:
        response += f"Варианты ответов:\n"
        for i, option in enumerate(options):
            prefix = "+" if i == correct_option else "   "
            response += f"{prefix} {i}. {option}\n"
    else:
        response += "Варианты ответов: нет\n"
    
    if correct_option is not None:
        response += f"\nПравильный ответ: вариант {correct_option}"
    
    await message.answer(response)

@router.message(Command("create_question"))
async def create_question_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer(
            "Использование: /create_question [JSON с данными вопроса]\n"
            'Пример: /create_question {"name": "Вопрос 1", "text": "2+2=?", "options": ["3", "4", "5"], "correct_option": 1}'
        )
        return
    
    try:
        question_data = json.loads(command.args)
        
        required_fields = ['name', 'text', 'options', 'correct_option']
        for field in required_fields:
            if field not in question_data:
                await message.answer(f"Отсутствует поле: {field}")
                return
        
        result, error = await make_authorized_request(chat_id, "POST", "/api/questions",
                                                     data=question_data)
        
        if error:
            await message.answer(f"Ошибка: {error}")
        else:
            question_id = result.get('question_id') if result else 'неизвестен'
            await message.answer(f"Вопрос создан! ID: {question_id}")
            
    except json.JSONDecodeError:
        await message.answer(
            "Неверный формат JSON\n\n"
            "Использование: /create_question [JSON с данными вопроса]\n"
            'Пример: /create_question {"name": "Вопрос 1", "text": "2+2=?", "options": ["3", "4", "5"], "correct_option": 1}'
)

@router.message(Command("update_question"))
async def update_question_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if not command or not command.args:
        await message.answer(
            "Использование: /update_question [question_id] [JSON]\n\n"
            'Пример: /update_question 1 {"name": "Новое название", "text": "Новый текст", "options": ["a", "b", "c"], "correct_option": 0}'
        )
        return
    
    try:
        args = command.args.strip().split(maxsplit=1)
        if len(args) != 2:
            await message.answer("Необходимо указать ID вопроса и JSON данные")
            return
        
        question_id, json_str = args[0], args[1]
        question_data = json.loads(json_str)
        
        result, error = await make_authorized_request(
            chat_id, "PUT", f"/api/questions/{question_id}",
            data=question_data
        )
        
        if error:
            await message.answer(f"Ошибка: {error}")
        else:
            new_version = result.get('version') if isinstance(result, dict) else 'новая версия'
            await message.answer(f"Вопрос {question_id} обновлен. Версия: {new_version}")
            
    except json.JSONDecodeError:
        await message.answer("Ошибка в формате JSON")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(Command("admin_help"))
async def admin_help_command(message: Message):
    help_text = """
Команды для учителей и администраторов:

Управление пользователями:
/users - список пользователей
/user_info [id] [type] - информация о пользователе
/set_name [id] [имя] - изменить имя пользователю
/user_roles [id] - показать роли
/user_roles [id] set [роли] - установить роли
/block_user [id] [true/false] - блокировка пользователей

Управление курсами:
/create_course [название] [описание] [instructor_id] - создать курс
/update_course [id] [название] [описание] - обновить курс
/delete_course [id] - удалить курс
/course_students [id] - студенты на курсе
/add_to_course [course_id] [user_id] - добавть студента на курс
/remove_from_course [course_id] [user_id] - отчислить студента с курса

Управление тестами:
/add_test [course_id] [название] - создать тест
/remove_test [course_id] [test_id] - убрать тест
/set_test_active [course_id] [test_id] [true/false] - активация теста
/test_results [test_id] - результаты теста

Управление вопросами:
/create_question [JSON] - создать вопрос
/update_question [JSON] - обновить вопрос
/my_questions - узнать мои вопросы
/add_to_test [test_id] [question_id] - добавить вопрос к тесту
    """
    
    await message.answer(help_text)