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
/login - войти
/logout - выйти
                                      
Для авторизованных:
/tests
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