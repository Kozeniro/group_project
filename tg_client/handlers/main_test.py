from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.token_utils import make_authorized_request

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
    courses, error = await make_authorized_request(chat_id, "GET", "/api/course")
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    if len(courses) > 0:
        response_text = "Доступные курсы:\n\n"
        for i in range(len(courses)):
            name = courses[i].get('name', 'Без названия')
            course_id = courses[i].get('id', '?')
            response_text += f"{i}. {name} (ID: {course_id})\n"
        await message.answer(response_text)
    else:
        await message.answer("Нет доступных курсов.")

@router.message(Command("profile"))
async def me_command(message: Message):
    chat_id = message.chat.id
    result, error = await make_authorized_request(chat_id, "GET", "/api/users/me")
    if error:
        await message.answer(f"Ошибка: {error}")
        return
    user_id = result.get('id', '?')
    name = result.get('name')
    email = result.get('email')
    
    await message.answer(
        f"**Ваш профиль**\n\n"
        f"ID: `{user_id}`\n"
        f"Имя: `{name}`\n"
        f"Email: `{email}`",
        parse_mode="Markdown"
    )