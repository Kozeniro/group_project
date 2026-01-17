from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.redis_utils import set_user_state, get_user_state

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] == 'unknown':
        set_user_state(chat_id, 'anonymous')
        await message.answer(
            "Привет! Это бот для авторизации и тестирования.\n"
            "Ваш статус: Анонимный\n"
            "Для доступа к тестам нужно авторизоваться: /login\n"
            "Команды: /help"
        )
    
    elif user_state['state'] == 'anonymous':
        await message.answer(
            "Вы в процессе авторизации.\n"
            "Статус: Анонимный\n"
            "Команды: /help"
        )
    
    else: 
        await message.answer(
            "Вы авторизованы. Доступные команды: /help"
        )


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("""
Доступные команды:

Для всех пользователей:
/start - начать работу
/help - помощь
/status - ваш текущий статус

Чтобы авторизороваться:
/register (/reg) [email] [password] - зарегистрироваться с почтой и паролем
/login (/l) - войти через GitHub или Яндекс
/login (/l) [email] [password] - войти c почтой и паролем

Для авторизованных:
/student_help - команды для студентов
/admin_help - команды для учителей(админов)
/id - узнать свой id
/name - узнать свое имя
/name [id] - узнать имя пользователя с id
/set_name [имя] - изменить своё имя
/profile - мой профиль
/check_blocked - проверить блокировку
/my_permissions - мои права
/refresh - обновить токены
/logout - выйти
/logout all=true - выйти на всех устройствах
/debug - отладочная информация
    """)

@router.message(Command("status"))
async def status_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)

    if user_state['state'] == 'unknown':
        await message.answer(f"Ваш статус: Неизвестный")
    elif user_state['state'] == 'anonymous':
        await message.answer(f"Ваш статус: Анонимный")
    else:
        await message.answer(f"Ваш статус: Авторизованный") 

    

@router.message()
async def unknown_command(message: Message):
    await message.answer("Нет такой команды.")