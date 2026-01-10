from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import secrets
import string

from utils.redis_utils import set_user_state, get_user_state, save_login_token

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
        token = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        user_state['login_token'] = token
        if user_state['state'] != 'anonymous':
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
            f"Токен: `{token}`"
            "Выберете способ входа:",
            reply_markup=keyboard
        )

@router.callback_query(F.data.startswith("github_"))
async def login_github(callback: CallbackQuery):
    token = callback.data.split("_")[1]
    
    await callback.message.answer(
        f"Авторизация через GitHub\n"
        f"Токен: `{token}`\n\n"
    )

@router.callback_query(F.data.startswith("yandex_"))
async def login_yandex(callback: CallbackQuery):
    token = callback.data.split("_")[1]
    
    await callback.message.answer(
        f"Авторизация через Яндекс\n"
        f"Токен: `{token}`\n\n"
    )

@router.callback_query(F.data.startswith("code_"))
async def login_code(callback: CallbackQuery):
    token = callback.data.split("_")[1]    

    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    
    await callback.message.answer(
        f"Вход по коду\n\n"
        f"Ваш код: {code}\n"
        f"Токен: `{token}`\n\n"
    )