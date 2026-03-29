from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Optional, Dict, Any
from collections import defaultdict
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
    
    attempt_result, attempt_error = await make_authorized_request(
        chat_id, "GET", "/api/attempt",
        params={"user_id": numeric_id, "test_id": test_id}
    )
    
    existing_attempt = None
    attempt_id = None
    
    if not attempt_error and attempt_result and isinstance(attempt_result, dict):
        status = attempt_result.get('status', '')
        if status == 'active':
            existing_attempt = attempt_result
            
            attempt_id = existing_attempt.get('id')
        elif status == 'completed':
            await message.answer("Вы уже потратили свою попытку.")
            return
    
    if existing_attempt and attempt_id:
        
        await message.answer("Продолжаем существующую попытку...")
        answers_list = existing_attempt.get('answers', [])
                
        test_result, test_error = await make_authorized_request(chat_id, "GET", f"/api/tests/{test_id}/questions")
        
        if test_error:
            await message.answer(f"Ошибка получения вопросов теста: {test_error}")
            return
        
        if isinstance(test_result, list):
            questions = test_result
        elif isinstance(test_result, dict):
            questions = test_result.get('questions', [])
        else:
            questions = []
        
        if not questions:
            await message.answer("В тесте нет вопросов")
            return
                
        saved_answers = {}  
        
        for answer in answers_list:
            if isinstance(answer, dict):
                question_id = answer.get('question_id')
                answer_id = answer.get('id')
                answer_option = answer.get('answer_option', -1)
                question_version = answer.get('question_version', 1)
                
                saved_answers[question_id] = {
                    'answer_id': answer_id,
                    'answer_option': answer_option,
                    'question_version': question_version
                }
                
        current_question_idx = 0
        for idx, question_id in enumerate(questions):
            answer_info = saved_answers.get(int(question_id))
            if answer_info and answer_info.get('answer_option', -1) == -1:
                current_question_idx = idx
                break
        
        session_data = {
            'test_id': test_id,
            'attempt_id': attempt_id,
            'user_id': numeric_id,
            'current_question': current_question_idx,
            'questions': questions,
            'answers': saved_answers,
            'is_continued': True
        }
    else:
        
        result, error = await make_authorized_request(
            chat_id, "POST", "/api/attempt",
            data={"user_id": int(numeric_id), "test_id": int(test_id)}
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
        
        attempt_id = None
        if isinstance(result, dict):
            attempt_id = result.get('attempt_id')
        elif isinstance(result, str):
            
            try:
                import json
                parsed = json.loads(result)
                if isinstance(parsed, dict):
                    attempt_id = parsed.get('attempt_id')
                elif isinstance(parsed, (int, str)):
                    attempt_id = str(parsed)
            except:                
                attempt_id = result
        
        test_result, test_error = await make_authorized_request(chat_id, "GET", f"/api/tests/{test_id}/questions")
        
        if test_error:
            await message.answer(f"Ошибка получения вопросов теста: {test_error}")
            return
        
        if isinstance(test_result, list):
            questions = test_result
        elif isinstance(test_result, dict):
            questions = test_result.get('questions', [])
        else:
            questions = []
        
        if not questions:
            await message.answer("В тесте нет вопросов")
            return
        
        attempt_info, attempt_info_error = await make_authorized_request(
            chat_id, "GET", "/api/attempt",
            params={"user_id": numeric_id, "test_id": test_id}
        )
        
        saved_answers = {}
        if not attempt_info_error and isinstance(attempt_info, dict):
            answers_list = attempt_info.get('answers', [])
            for answer in answers_list:
                if isinstance(answer, dict):
                    question_id = answer.get('question_id')
                    answer_id = answer.get('id')
                    answer_option = answer.get('answer_option', -1)
                    question_version = answer.get('question_version', 1)
                    
                    saved_answers[question_id] = {
                        'answer_id': answer_id,
                        'answer_option': answer_option,
                        'question_version': question_version
                    }
        
        session_data = {
            'test_id': test_id,
            'attempt_id': attempt_id,
            'user_id': numeric_id,
            'current_question': 0,
            'questions': questions,
            'answers': saved_answers,
            'is_continued': False
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
    
    question_id = int(questions[current_idx])
    answer_info = session_data['answers'].get(question_id, {})
    previous_answer = answer_info.get('answer_option', -1)
    question_version = answer_info.get('question_version', 1)
    
    result, error = await make_authorized_request(
        chat_id, "GET", f"/api/questions/{question_id}",
        params={"version": question_version}
    )
    
    if error:
        await message.answer(f"Ошибка получения вопроса: {error}")
        return
    
    if isinstance(result, dict):
        question_text = result.get('text', '')
        options = result.get('options', [])
        name = result.get('name', '')
    else:
        await message.answer(f"Неверный формат вопроса: {result}")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    if isinstance(options, list) and options:
        for idx, option_text in enumerate(options):
            
            prefix = "✅ " if idx == previous_answer else ""
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"{prefix}{idx + 1}: {option_text}",
                    callback_data=f"answer_{idx}"
                )
            ])
    else:
        
        prefix1 = "✅ " if previous_answer == 0 else ""
        prefix2 = "✅ " if previous_answer == 1 else ""
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"{prefix1}Да", callback_data="answer_0")
        ])
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"{prefix2}Нет", callback_data="answer_1")
        ])    
    
    nav_buttons = []
    if current_idx > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data="nav_prev"))
    
    if current_idx < len(questions) - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data="nav_next"))
    
    if nav_buttons:
        keyboard.inline_keyboard.append(nav_buttons)
        
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Завершить тест", callback_data="finish_test")
    ])
    
    session_data['current_question_id'] = question_id
    session_data['current_answer_info'] = answer_info
    
    test_sessions[chat_id] = session_data
    
    question_num = current_idx + 1
    total_questions = len(questions)
    progress = f"({question_num}/{total_questions})"
    
    message_text = f"Вопрос {progress}"
    if name:
        message_text += f": {name}"
    message_text += f"\n\n{question_text}"
    
    await message.answer(message_text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext = None):
    chat_id = callback.from_user.id
    answer_idx = callback.data.split("_")[1]
    
    if chat_id not in test_sessions:
        await callback.answer("Сессия теста не найдена")
        return
    
    session_data = test_sessions[chat_id]
    question_id = session_data['current_question_id']
    answer_info = session_data['current_answer_info']
    
    try:
        answer_num = int(answer_idx)
    except ValueError:
        answer_num = 0
        
    answer_id = answer_info.get('answer_id')
    
    if not answer_id:
        await callback.answer("Ошибка: не найден ID ответа")
        return    
    
    update_result, update_error = await make_authorized_request(
        chat_id, "PUT", f"/api/answers/{answer_id}",
        data={"answer_option": answer_num}
    )
    
    if update_error:
        await callback.answer(f"Ошибка сохранения ответа: {update_error}")
        return
    
    
    session_data['answers'][question_id]['answer_option'] = answer_num
    test_sessions[chat_id] = session_data
    
    await callback.answer(f"Ответ сохранен: вариант {answer_num + 1}")
        

@router.callback_query(F.data == "finish_test")
async def finish_test_handler(callback: CallbackQuery):
    chat_id = callback.from_user.id
    
    if chat_id not in test_sessions:
        await callback.answer("Сессия теста не найдена")
        return
    
    session_data = test_sessions[chat_id]
    await callback.message.delete()
    
    
    attempt_id = session_data.get('attempt_id')
    if not attempt_id:
        await callback.message.answer("Ошибка: не найден ID попытки")
        if chat_id in test_sessions:
            del test_sessions[chat_id]
        return
    
    await finish_test(callback.message, session_data)

async def finish_test(message: Message, session_data: Dict):
    chat_id = message.chat.id
    attempt_id = session_data.get('attempt_id')
    
    if not attempt_id:
        await message.answer("Ошибка: не удалось получить ID попытки для завершения")
        if chat_id in test_sessions:
            del test_sessions[chat_id]
        return
    
    
    result, error = await make_authorized_request(
        chat_id, "DELETE", f"/api/attempt/{attempt_id}"
    )
    
    if error:
        if "404" in error:
            await message.answer("Попытка уже завершена или не найдена")
        else:
            await message.answer(f"Ошибка завершения теста: {error}")
    else:
        await message.answer("Тест завершен! Результаты будут доступны позже.")
    
    if chat_id in test_sessions:
        del test_sessions[chat_id]


@router.callback_query(F.data == "nav_prev")
async def nav_prev_handler(callback: CallbackQuery):
    chat_id = callback.from_user.id
    
    if chat_id not in test_sessions:
        await callback.answer("Сессия теста не найдена")
        return
    
    session_data = test_sessions[chat_id]
    if session_data['current_question'] > 0:
        session_data['current_question'] -= 1
        test_sessions[chat_id] = session_data
        await callback.message.delete()
        await show_question(callback.message, session_data)
    else:
        await callback.answer("Это первый вопрос")

@router.callback_query(F.data == "nav_next")
async def nav_next_handler(callback: CallbackQuery):
    chat_id = callback.from_user.id
    
    if chat_id not in test_sessions:
        await callback.answer("Сессия теста не найдена")
        return
    
    session_data = test_sessions[chat_id]
    if session_data['current_question'] < len(session_data['questions']) - 1:
        session_data['current_question'] += 1
        test_sessions[chat_id] = session_data
        await callback.message.delete()
        await show_question(callback.message, session_data)
    else:
        await callback.answer("Это последний вопрос")

@router.message(Command("scores"))
async def scores_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    if not command or not command.args:
        id_result, id_error = await make_authorized_request(chat_id, "GET", "/api/user_id")
        response = "Ваши оценки за тесты:\n\n"
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
        if not numeric_id:
            await message.answer("Не удалось получить ваш ID")
            return
    
    else:
        numeric_id = command.args.strip()   
        response = f"Оценки пользователя {numeric_id} за тесты:\n\n"

    
    courses_result, courses_error = await make_authorized_request(
        chat_id, "GET", f"/api/users/{numeric_id}/info",
        params={"info_type": "courses"}
    )
    
    if courses_error:
        await message.answer(f"Ошибка получения курсов: {courses_error}")
        return
    
    if not courses_result:
        await message.answer("Нет курсов")
        return    
    
    seen_scores = set()  
    all_scores = []
    
    try:
        
        all_courses_result, all_courses_error = await make_authorized_request(
            chat_id, "GET", "/api/course"
        )
        
        course_name_to_id = {}
        if not all_courses_error and isinstance(all_courses_result, list):
            for course in all_courses_result:
                if isinstance(course, dict):
                    course_id = course.get('id')
                    course_name = course.get('name')
                    if course_id and course_name:
                        course_name_to_id[course_name] = course_id
        
        
        if isinstance(courses_result, list):
            for course_item in courses_result:
                course_name = None
                course_id = None
                
                if isinstance(course_item, dict):
                    
                    course_id = course_item.get('id')
                    course_name = course_item.get('name', f'Курс {course_id}')
                elif isinstance(course_item, str):
                    
                    course_name = course_item
                    course_id = course_name_to_id.get(course_name)
                elif isinstance(course_item, (int, float)):
                    
                    course_id = str(course_item)
                    course_name = f'Курс {course_id}'
                
                if not course_name:
                    course_name = f'Курс {course_id}' if course_id else 'Неизвестный курс'
                
                if course_id:
                    
                    tests_result, tests_error = await make_authorized_request(
                        chat_id, "GET", f"/api/course/{course_id}/tests"
                    )
                    
                    if not tests_error and tests_result:
                        tests_list = []
                        
                        if isinstance(tests_result, list):
                            tests_list = tests_result
                        elif isinstance(tests_result, dict) and 'tests' in tests_result:
                            tests_list = tests_result['tests']
                        
                        unique_tests = {}
                        for test in tests_list:
                            if isinstance(test, dict):
                                test_id = test.get('id')
                                if test_id:
                                    unique_tests[test_id] = test
                        
                        for test_id, test in unique_tests.items():
                            test_name = test.get('name', f'Тест {test_id}')
                            
                            scores_result, scores_error = await make_authorized_request(
                                chat_id, "GET", f"/api/tests/{test_id}/scores"
                            )
                            
                            if not scores_error and scores_result:
                                scores_list = []
                                
                                if isinstance(scores_result, list):
                                    scores_list = scores_result
                                elif isinstance(scores_result, dict) and 'scores' in scores_result:
                                    scores_list = scores_result['scores']
                                user_score = None
                                for score_data in scores_list:
                                    if isinstance(score_data, dict):
                                        user_id = score_data.get('user_id')
                                        score = score_data.get('score')
                                        if str(user_id) == str(numeric_id) and score is not None:
                                            user_score = score
                                            break
                                
                                if user_score is not None:
                                    
                                    score_key = (course_name, test_id)
                                    if score_key not in seen_scores:
                                        seen_scores.add(score_key)
                                        all_scores.append({
                                            'course_name': course_name,
                                            'test_name': test_name,
                                            'test_id': test_id,
                                            'score': user_score
                                        })
        
        if not all_scores:
            await message.answer(
                "Пока нет оценок за тесты.\n\n"
                "Возможные причины:\n"
                "1. Тест еще не пройден\n"
                "2. Тесты еще не проверены\n"
                "3. Нет доступных данных об оценках"
            )
            return
        
        
        scores_by_course = defaultdict(list)
        
        for score_data in all_scores:
            scores_by_course[score_data['course_name']].append(score_data)
                
        for course_name, test_scores in scores_by_course.items():
            response += f"Курс {course_name}:\n"      
            
            unique_test_scores = {}
            for score_data in test_scores:
                test_id = score_data['test_id']
                if test_id not in unique_test_scores:
                    unique_test_scores[test_id] = score_data    
            
            for test_id, score_data in unique_test_scores.items():
                test_name = score_data['test_name']
                score = score_data['score']
                test_info, test_error = await make_authorized_request(
                    chat_id, "GET", f"/api/tests/{test_id}/questions"
                )
                total_questions = len(test_info)
                response += f"(ID {test_id}) {test_name}: {score}/{total_questions}\n"
        
        numeric_scores = []
        for score_data in all_scores:
            try:
                score_num = float(score_data['score'])
                numeric_scores.append(score_num)
            except (ValueError, TypeError):
                continue
        await message.answer(response)

    except Exception as e:
        await message.answer(f"Ошибка при получении оценок: {e}")

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
    
    await message.answer("Получаю ваши попытки...")
    
    
    courses_result, courses_error = await make_authorized_request(
        chat_id, "GET", f"/api/users/{numeric_id}/info",
        params={"info_type": "courses"}
    )
    
    if courses_error:
        await message.answer(f"Ошибка получения курсов: {courses_error}")
        return
    
    response = "Ваши попытки прохождения тестов:\n\n"
    
    if isinstance(courses_result, list) and courses_result:
        for course_item in courses_result:
            course_name = None
            
            if isinstance(course_item, dict):
                course_name = course_item.get('name')
            elif isinstance(course_item, str):
                course_name = course_item
            
            if course_name:
                response += f"📚 {course_name}:\n"
                
                response += "  (информация о попытках)\n\n"
    else:
        response += "У вас нет курсов или попыток прохождения тестов."
    
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
/scores - мои оценки
/questions - список вопросов
/question_info [question_id] [version] - информация о вопросе
/start_test [id] - начать тест
/my_attempts - мои попытки
    """
    
    await message.answer(help_text)