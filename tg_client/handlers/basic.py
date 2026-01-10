from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from utils.redis_utils import set_user_state, get_user_state, delete_user_state
from utils.auth_client import auth_client

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


@router.message(Command("logout"))
async def logout_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)

    if user_state['state'] != 'authorized':
        await message.answer("Вы не авторизованы.")
        return
    if command and command.args and "all=true" in command.args:
        refresh_token = user_state.get('refresh_token')
        if refresh_token:
            await auth_client.logout(refresh_token)
        delete_user_state(chat_id)
        await message.answer("Сеанс завершён на всех устройствах.")
    else:
        delete_user_state(chat_id)
        await message.answer("Сеанс завершён.") 
    

@router.message(Command("refresh"))
async def refresh_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)

    if user_state['state'] != 'authorized':
        await message.answer("Вы не авторизованы.")
        return    
    refresh_token = user_state.get('refresh_token')
    if not refresh_token:
        await message.answer("Нет токена для обновления.")
        return    
    
    result = await auth_client.refresh_access_token(refresh_token)    
    access_token = result.get('access_token')
    new_refresh_token = result.get('refresh_token')

    user_state['access_token'] = access_token
    user_state['refresh_token'] = new_refresh_token
    set_user_state(chat_id, 'authorized', user_state)
    await message.answer("Токены обновлены.")


@router.message(Command("tests"))
async def tests_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)

    if user_state['state'] != 'authorized':
        await message.answer("Вы не авторизованы.")
    else:
        await message.answer("Доступные тесты: [потом будет]") 
    

@router.message()
async def unknown_command(message: Message):
    await message.answer("Нет такой команды.")