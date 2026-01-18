from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Optional, Dict, Any
import json

from utils.redis_utils import get_user_state, set_user_state
from utils.token_utils import make_authorized_request
import jwt

router = Router()

class TestTaking(StatesGroup):
    waiting_for_answer = State()
    current_test = State()
    current_question = State()
    answers = State()

test_sessions = {}

@router.message(Command("start_test"))
async def start_test_command(message: Message, command: CommandObject = None, state: FSMContext = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer("Использование: /start_test [test_id]")
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

    await message.answer(f"Начинаем тест {test_id}...")
    
    result, error = await make_authorized_request(
        chat_id, "POST", "/api/attempt",
        data={"user_id": numeric_id, "test_id": int(test_id)}
    )
    
    if error:
        if "500" in error:
            await message.answer(
                "Ошибка начала теста.\n\n"
                "Возможные причины:\n"
                "1. Тест не существует\n"
                "2. Тест не активен\n"
                "3. У вас уже есть активная попытка\n"
                "4. Вы не записаны на курс с этим тестом"
            )
        else:
            await message.answer(f"Ошибка начала теста: {error}")
        return
    
    attempt_id = result.get('attempt_id')
    if not attempt_id:
        await message.answer("Не удалось создать попытку")
        return
        
    test_result, error = await make_authorized_request(chat_id, "GET", f"/api/tests/{test_id}/questions")
    
    questions = test_result.get('questions', [])
    if not questions:
        await message.answer("В тесте нет вопросов")
        return
    
    session_data = {
        'test_id': test_id,
        'attempt_id': attempt_id,
        'user_id': numeric_id,
        'current_question': 0,
        'questions': questions,
        'answers': {}
    }
    
    test_sessions[chat_id] = session_data
    
    if state:
        await state.set_state(TestTaking.waiting_for_answer)
        await state.set_data(session_data)  
    
    await show_question(message, session_data)

async def show_question(message: Message, session_data: Dict):
    chat_id = message.chat.id
    current_idx = session_data['current_question']
    questions = session_data['questions']
    
    if current_idx >= len(questions):
        await finish_test(message, session_data)
        return
    
    question_id = questions[current_idx]
    
    result, error = await make_authorized_request(chat_id, "GET", f"/api/questions/{question_id}")
    
    if error:
        await message.answer(f"Ошибка получения вопроса: {error}")
        return
    
    question_text = result.get('text', '')
    options = result.get('options', {})
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for key, option_text in options.items():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{key}: {option_text}",
                callback_data=f"answer_{key}"
            )
        ])
    
    session_data['current_question_id'] = question_id
    session_data['current_options'] = options
    
    test_sessions[chat_id] = session_data
    
    await message.answer(
        f"Вопрос {current_idx + 1} из {len(questions)}:\n\n{question_text}",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext = None):
    chat_id = callback.message.chat.id
    answer_key = callback.data.split("_")[1]
    
    if chat_id not in test_sessions:
        await callback.message.answer("Сессия теста не найдена. Начните заново: /start_test [test_id]")
        return
    
    session_data = test_sessions[chat_id]
    question_id = session_data['current_question_id']
    attempt_id = session_data['attempt_id']
    
    answer_num = int(answer_key) if answer_key.isdigit() else 0
    
    result, error = await make_authorized_request(chat_id, "POST", f"/api/answers",
                                                 data={"attempt_id": attempt_id, "question_id": question_id})
    
    if error and "уже существует" not in str(error).lower():
        await callback.message.answer(f"Ошибка создания ответа: {error}")
        return
    
    answer_id = None
    if result and isinstance(result, dict):
        answer_id = result.get('id')
    
    if answer_id:
        update_result, update_error = await make_authorized_request(chat_id, "PUT", f"/api/answers/{answer_id}",
                                                                   data={"answer_option": answer_num})
        
        if update_error:
            await callback.message.answer(f"Ошибка сохранения ответа: {update_error}")
            return
    
    session_data['answers'][question_id] = answer_num
    session_data['current_question'] += 1
    
    await callback.message.delete()
    
    if session_data['current_question'] >= len(session_data['questions']):
        await finish_test(callback.message, session_data)
    else:
        test_sessions[chat_id] = session_data
        if state:
            await state.set_data(session_data)
        await show_question(callback.message, session_data)

async def finish_test(message: Message, session_data: Dict):
    chat_id = message.chat.id
    attempt_id = session_data['attempt_id']
    
    result, error = await make_authorized_request(chat_id, "DELETE", f"/api/attempt/{attempt_id}")
    
    if error:
        await message.answer(f"Ошибка завершения теста: {error}")
    else:
        await message.answer("Тест завершен! Результаты будут доступны позже.")
    
    if chat_id in test_sessions:
        del test_sessions[chat_id]

@router.message(Command("my_attempts"))
async def my_attempts_command(message: Message):
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
    
    courses_result, courses_error = await make_authorized_request(chat_id, "GET", f"/api/users/{numeric_id}/info",
                                                                 params={"info_type": "courses"})
    
    if courses_error:
        await message.answer(f"Ошибка получения курсов: {courses_error}")
        return
    
    if not courses_result:
        await message.answer("У вас нет курсов")
        return
    
    response = "Ваши попытки:\n\n"
    
    for course in courses_result:
        course_id = course.get('id')
        course_name = course.get('name', 'Без названия')
        
        tests_result, tests_error = await make_authorized_request(chat_id, "GET", f"/api/course/{course_id}/tests")
        
        if not tests_error and tests_result:
            for test in tests_result:
                test_id = test.get('id')
                test_name = test.get('name', 'Без названия')
                
                attempt_result, attempt_error = await make_authorized_request(chat_id, "GET", f"/api/attempt",
                                                                             params={"user_id": numeric_id, "test_id": test_id})
                
                if not attempt_error and attempt_result:
                    status = attempt_result.get('status', 'неизвестно')
                    response += f"{course_name} - {test_name}: {status}\n"
    
    if response == "Ваши попытки:\n\n":
        response += "У вас нет завершенных попыток"
    
    await message.answer(response)

@router.message(Command("join_course"))
async def join_course_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer(
            "Использование: /join_course [course_id]\n\n"
            "Сначала посмотрите доступные курсы: /courses"
        )
        return
    
    course_id = command.args.strip()    
    
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
    
    course_info, course_error = await make_authorized_request(
        chat_id, "GET", f"/api/course/{course_id}/info"
    )
    
    if course_error:
        await message.answer(f"Курс {course_id} не найден: {course_error}")
        return
    
    course_name = course_info.get('name', 'Без названия')
    instructor_id = course_info.get('instructor_id')
        
    students_result, students_error = await make_authorized_request(
        chat_id, "GET", f"/api/course/{course_id}/students"
    )
    
    if not students_error and isinstance(students_result, list):
        if str(numeric_id) in [str(sid) for sid in students_result]:
            await message.answer(f"Вы уже записаны на курс '{course_name}'")
            return
        
    result, error = await make_authorized_request(
        chat_id, "POST", f"/api/course/{course_id}/students",
        data={"user_id": numeric_id}  
    )
    
    if error:
        if "500" in error:            
            await message.answer("Ошибка при записи на курс.")
        else:
            await message.answer(f"Ошибка: {error}")
    else:
        await message.answer(f"Вы успешно записаны на курс '{course_name}'!")


@router.message(Command("leave_course"))
async def leave_course_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
        await message.answer("Использование: /leave_course [course_id]")
        return
    
    course_id = command.args.strip()
    
    id_result, id_error = await make_authorized_request(chat_id, "GET", "/api/user_id")
    
    if id_error:
        await message.answer(f"Не удалось получить ваш ID: {id_error}")
        return
    
    if isinstance(id_result, dict):
        numeric_id = id_result.get('user_id')
    else:
        numeric_id = str(id_result) if id_result else None
    
    students_result, students_error = await make_authorized_request(
        chat_id, "GET", f"/api/course/{course_id}/students"
    )
    
    is_enrolled = False
    if not students_error and isinstance(students_result, list):
        is_enrolled = str(numeric_id) in [str(sid) for sid in students_result]
    
    if not is_enrolled:
        await message.answer(f"Вы не записаны на курс {course_id}")
        return
    
    result, error = await make_authorized_request(
        chat_id, "DELETE", f"/api/course/{course_id}/students",
        data={"user_id": numeric_id}
    )
    
    if error:
        if "404" in error:
            await message.answer(f"Не удалось выйти с курса {course_id}")
        else:
            await message.answer(f"Ошибка выхода с курса: {error}")
    else:
        await message.answer(f"Вы успешно вышли с курса {course_id}!")


@router.message(Command("name"))
async def get_name_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    if not command or not command.args:
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
            chat_id, "GET", f"/api/users/{numeric_id}/name"
        )
        
        if error:
            if "404" in error:
                await message.answer("Ваше имя не установлено. Используйте /set_name [имя]")
            else:
                await message.answer(f"Ошибка: {error}")
        else:
            name = result.get('name') if isinstance(result, dict) else str(result)
            await message.answer(f"Ваше имя: {name}")
        return
    
    target_user_id = command.args.strip()
    
    result, error = await make_authorized_request(
        chat_id, "GET", f"/api/users/{target_user_id}/name"
    )
    
    if error:
        if "404" in error:
            await message.answer(f"Пользователь {target_user_id} не найден или имя не установлено")
        elif "403" in error:
            await message.answer(f"Нет прав для просмотра имени пользователя {target_user_id}")
        else:
            await message.answer(f"Ошибка: {error}")
    else:
        name = result.get('name') if isinstance(result, dict) else str(result)
        await message.answer(f"Имя пользователя {target_user_id}: {name}")


@router.message(Command("check_blocked"))
async def check_blocked_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    
    if not command or not command.args:
        
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
        
        target_id = str(numeric_id)
        check_self = True
    else:        
        target_id = command.args.strip()
    
    result, error = await make_authorized_request(
        chat_id, "GET", f"/api/users/{target_id}/blocked"
    )
    
    if error:
        if "404" in str(error):
            await message.answer(f"Информация о блокировке пользователя {target_id} не найдена")
        elif "403" in str(error):
            await message.answer(f"Нет прав для просмотра блокировки пользователя {target_id}")
        else:
            await message.answer(f"Ошибка: {error}")
    else:
        blocked = result.get('blocked', False) if isinstance(result, dict) else result
        status = "заблокирован" if blocked else "не заблокирован"
        pronoun = "Ваш статус" if check_self else f"Статус пользователя {target_id}"
        await message.answer(f"{pronoun}: {status}")

@router.message(Command("student_help"))
async def user_help_command(message: Message):
    help_text = """
Команды для студентов:

/courses - все курсы
/mycourses - мои курсы
/course [id] - информация о курсе
/join_course [id] - записаться на курс
/leave_course [id] - покинуть курс
/tests [id] - узнать тесты на курсе
/mytests - мои тесты
/myscores - мои оценки
/questions - список вопросов
/question_info [question_id] [version] - информация о вопросе
/start_test [id] - начать тест
/my_attempts - мои попытки
    """
    
    await message.answer(help_text)