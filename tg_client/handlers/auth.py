from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import secrets
import string
from datetime import datetime

from utils.redis_utils import set_user_state, get_user_state, delete_user_state, save_login_token, get_login_token, delete_login_token
from utils.auth_client import auth_client

router = Router()

@router.message(Command("login"))
async def login_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] == 'unknown':
        await message.answer("Сначала напишите /start")    
    elif user_state['state'] == 'authorized':
        await message.answer("Вы уже авторизованы!")
    else: 
        result = await auth_client.create_login_token(provider="default")       
        token = result.get('token')
        
        user_state['login_token'] = token
        user_state['state'] = 'anonymous'
        set_user_state(chat_id, user_state['state'], user_state)
        save_login_token(token, chat_id)
                    
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="GitHub", 
                    callback_data=f"github_{token}"
                ),
                InlineKeyboardButton(
                    text="Яндекс", 
                    callback_data=f"yandex_{token}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Войти по коду", 
                    callback_data=f"code_{token}"
                )
            ]
        ])

        await message.answer(
            "Выберите способ входа:",
            reply_markup=keyboard
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
        "Для авторизации через GitHub перейдите по ссылке:\n\n"
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
        "Для авторизации через Яндекс перейдите по ссылке:\n\n"
        "После авторизации нажмите Проверить статус.",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("code_"))
async def login_code(callback: CallbackQuery):
    token = callback.data.split("_")[1]   

    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    save_login_token(f"code_{code}", {
        'original_token': token,
        'chat_id': callback.from_user.id,
        'created_at': datetime.now().isoformat()
    })

    await callback.message.answer(
        f"Вход по коду\n\n"
        f"Ваш код: {code}\n"
        f"Токен: `{token}`\n\n"
        "Введите этот код на другом авторизованном устройстве.\n"
        "Код действителен 5 минут."
    )

@router.callback_query(F.data.startswith("check_"))
async def check_status(callback: CallbackQuery):    
    token = callback.data.split("_")[1]
    chat_id = callback.from_user.id
    
    status_data = await auth_client.check_login_status(token)
    status = status_data.get('status', 'unknown')

    status = status_data.get('status', 'unknown')


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
            'authorized_at': datetime.now().isoformat()
        })
        
        delete_login_token(token)

        await callback.message.answer(
            "Успешная авторизация.\n"
            f"User ID: `{user_id}`"
        )    
    elif status == 'expired':
        delete_user_state(chat_id)
        await callback.message.answer(
            "Токен устарел. Начните авторизацию заново."
        )
    elif status == 'denied':
        delete_user_state(chat_id)        
        await callback.message.answer(
            "Авторизация отклонена.\n"
            "Попробуйте снова: /login"
        )

@router.message(Command("enter_code"))
async def enter_code_command(message: Message, command: CommandObject = None):    
    code = command.args.strip()
    chat_id = message.chat.id
    
    code_data = get_login_token(f"code_{code}")
    if not code_data:
        await message.answer("Код не найден или устарел.")
        return
    
    original_token = code_data.get('original_token')    
    result = await auth_client.login_with_code(code, original_token)
    
    access_token = result.get('access_token')
    refresh_token = result.get('refresh_token')
    user_id = result.get('user_id')        

    set_user_state(chat_id, 'authorized', {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': user_id,
        'authorized_at': datetime.now().isoformat()
    })            
    await message.answer(
        "Успешная авторизация.\n"
        f"User ID: `{user_id}`"
    )
