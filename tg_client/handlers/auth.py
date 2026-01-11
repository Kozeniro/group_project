from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import json

from utils.redis_utils import set_user_state, get_user_state, delete_user_state, save_login_token, get_login_token, delete_login_token
from utils.auth_client import auth_client

router = Router()

@router.message(Command("login"))
async def login_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] == 'authorized':
        await message.answer("Вы уже авторизованы.")
        return
    
    result = await auth_client.create_login_token()
    login_token = result['login_token']
    
    set_user_state(chat_id, 'anonymous', {
        'login_token': login_token,
        'created_at': datetime.now().isoformat()
    })
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="GitHub",
                callback_data=f"github_{login_token}"
            ),
            InlineKeyboardButton(
                text="Яндекс", 
                callback_data=f"yandex_{login_token}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Войти по коду",
                callback_data=f"create_code_{login_token}"
            )
        ]
    ])
    
    await message.answer(
        "Выберите способ входа:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("create_code_"))
async def create_code_login(callback: CallbackQuery):
    original_token = callback.data.split("_")[2]
    chat_id = callback.from_user.id
        
    result = await auth_client.create_login_token("code")
    
    login_token = result['login_token']
    code = result.get('code')

    set_user_state(chat_id, 'anonymous', {
        'login_token': login_token,
        'code': code,
        'created_at': datetime.now().isoformat()
    })
    
    save_login_token(f"code_{code}", {
        'login_token': login_token,
        'chat_id': chat_id,
        'created_at': datetime.now().isoformat(),
        'status': 'pending'
    })
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Проверить статус",
            callback_data=f"check_{login_token}"
        )]
    ])
    
    await callback.message.answer(
        "Вход по коду\n\n"
        f"Ваш код: `{code}`\n"
        "Инструкция:\n"
        "На другом авторизованном устройстве введите команду:\n"
        f"   `/enter_code {code}`\n"
        "После ввода кода нажмите Проверить статус\n\n"
        "Код действителен 1 минуту",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@router.message(Command("enter_code"))
async def enter_code_command(message: Message, command: CommandObject = None):
    if not command or not command.args:
        await message.answer(
            "Использование: `/enter_code <код>`\n"
            "Пример: `/enter_code 123456`",
            parse_mode="Markdown"
        )
        return
    
    code = command.args.strip()
    
    if not code.isdigit() or len(code) != 6:
        await message.answer("Код должен состоять из 6 цифр")
        return
    
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer(
            "Вы не авторизованы на этом устройстве."
        )
        return
    
    refresh_token = user_state.get('refresh_token')
        
    result = await auth_client.verify_code(code, refresh_token)
    
    if result.get('success'):
        await message.answer(
            "Код Верный!\n"
            "Авторизация выполнена."
        )
    else:
        error_msg = result.get('error', 'Неизвестная ошибка')
        
        await message.answer(
            f"Ошибка: {error_msg}\n\n"
            "Возможные причины:\n"
            "-Код неверный\n"
            "-Код устарел (время действия 1 минута)\n"
            "-Код уже был использован"
        )

@router.callback_query(F.data.startswith("github_"))
async def login_github(callback: CallbackQuery):
    token = callback.data.split("_")[1]
    
    auth_url = await auth_client.get_github_auth_url(token)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Авторизация через GitHub", 
            url=auth_url
        )],
        [InlineKeyboardButton(
            text="Проверить статус", 
            callback_data=f"check_{token}"
        )]
    ])
    
    await callback.message.answer(
        "Для авторизации через GitHub перейдите по ссылке ниже:\n\n"
        "После авторизации нажмите Проверить статус.",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("yandex_"))
async def login_yandex(callback: CallbackQuery):
    token = callback.data.split("_")[1]
    
    auth_url = await auth_client.get_yandex_auth_url(token)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Авторизация через Яндекс", 
            url=auth_url
        )],
        [InlineKeyboardButton(
            text="Проверить статус", 
            callback_data=f"check_{token}"
        )]
    ])
    
    await callback.message.answer(
        "Для авторизации через Яндекс перейдите по ссылке ниже:\n\n"
        "После авторизации нажмите 'Проверить статус'.",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("check_"))
async def check_status(callback: CallbackQuery):
    token = callback.data.split("_")[1]
    chat_id = callback.from_user.id
        
    status_data = await auth_client.check_login_status(token)
    
    status = status_data.get('status')
   
    if status == "pending":
        await callback.message.answer("Авторизация еще не завершена.")      
    elif status == 'authorized':
        access_token = status_data.get('access_token')
        refresh_token = status_data.get('refresh_token')
        user_id = status_data.get('user_id')

        set_user_state(chat_id, 'authorized', {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'authorized_at': datetime.now().isoformat(),
            'login_token': None 
        })
        
        user_state = get_user_state(chat_id)
        if 'code' in user_state:
            code = user_state['code']
            delete_login_token(f"code_{code}")
        
        await callback.message.answer(
            "Успешная авторизация.\n"
            f"User ID: `{user_id}`"
        )
    
    elif status == 'expired':
        delete_user_state(chat_id)
        await callback.message.answer(
            "Токен устарел. Начните авторизацию заново: /login"
        )    
    elif status == 'denied':
        delete_user_state(chat_id)
        await callback.message.answer(
            "Авторизация отклонена.\n"
            "Попробуйте снова: /login"
        )


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

