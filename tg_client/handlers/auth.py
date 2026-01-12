from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import json

from utils.redis_utils import set_user_state, get_user_state, delete_user_state, save_login_token, get_login_token, delete_login_token
from utils.auth_client import auth_client

router = Router()

async def delete_and_send(message_or_callback, text, **kwargs):
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.delete()
        return await message_or_callback.message.answer(text, **kwargs)
    else:
        return await message_or_callback.answer(text, **kwargs)


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
                callback_data=f"get_code_{login_token}"
            )
        ]
    ])
    
    await message.answer(
        "Выберите способ входа:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("get_code_"))
async def get_code_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[2]
    chat_id = callback.from_user.id
    result = await auth_client.get_code_for_token(login_token)
    
    code = result['code']
    expires_in = result.get('expires_in', 60)
    
    user_state = get_user_state(chat_id)
    user_state['code'] = code
    user_state['code_expires_in'] = expires_in
    set_user_state(chat_id, 'anonymous', user_state)
    
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
    
    await delete_and_send(
        callback,
        "Вход по коду\n\n"
        f"Ваш код: `{code}`\n"
        "Инструкция:\n"
        "На другом авторизованном устройстве введите команду:\n"
        f"`/enter_code {code}`\n"
        "После ввода кода нажмите Проверить статус\n\n"
        "Код действителен 1 минуту",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("github_"))
async def github_login_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    chat_id = callback.from_user.id
    
    auth_url = await auth_client.get_github_auth_url(login_token)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Авторизация через GitHub", 
            url=auth_url
        )],
        [InlineKeyboardButton(
            text="Получить код", 
            callback_data=f"get_gh_code_{login_token}"
        )],
        [InlineKeyboardButton(
            text="Проверить статус", 
            callback_data=f"check_{login_token}"
        )]
    ])
    
    await delete_and_send(
        callback,
        "Авторизация через GitHub:\n\n"
        "1. Перейдите по ссылке ниже\n"
        "2. Авторизуйтесь в GitHub\n"
        "3. После авторизации нажмите 'Получить код'\n"
        "4. Введите код командой `/enter_code <код>`\n"
        "5. Проверьте статус",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("get_gh_code_"))
async def get_github_code_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[3]
    chat_id = callback.from_user.id
    
    result = await auth_client.get_code_for_token(login_token)
    
    if not result or 'code' not in result:
        await callback.message.answer(
            "Не удалось получить код."
        )
        return
    
    code = result['code']
    
    user_state = get_user_state(chat_id)
    user_state['code'] = code
    set_user_state(chat_id, 'anonymous', user_state)
    
    save_login_token(f"code_{code}", {
        'login_token': login_token,
        'chat_id': chat_id,
        'created_at': datetime.now().isoformat(),
        'status': 'pending',
        'source': 'github'
    })
    
    await delete_and_send(
        callback,
        "Код получен:\n\n"
        f"`{code}`\n\n"
        "Введите команду:**\n"
        f"`/enter_code {code}`\n\n"
        "Код действителен 1 минуту",
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("yandex_"))
async def yandex_login_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    
    auth_url = await auth_client.get_yandex_auth_url(login_token)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Авторизация через Яндекс", 
            url=auth_url
        )],
        [InlineKeyboardButton(
            text="Проверить статус", 
            callback_data=f"check_{login_token}"
        )]
    ])
    
    await delete_and_send(
        callback,
        "Авторизация через Яндекс:\n\n"
        "1. Перейдите по ссылке ниже\n"
        "2. Авторизуйтесь в Яндекс\n"
        "3. После авторизации нажмите 'Получить код'\n"
        "4. Введите код командой `/enter_code <код>`\n"
        "5. Проверьте статус",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@router.message(Command("enter_code"))
async def enter_code_command(message: Message, command: CommandObject = None):
    if not command or not command.args:
        await message.answer(
            "Использование: /enter_code <код>"
        )
        return
    
    code = command.args.strip()
    chat_id = message.chat.id
    
    if not code.isdigit() or len(code) != 6:
        await message.answer("Код должен состоять из 6 цифр")
        return
    
    result = await auth_client.verify_code(code)
    
    if result.get('success'):
        data = result.get('data', {})
        
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        user_id = data.get('user_id')
        
        set_user_state(chat_id, 'authorized', {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'authorized_at': datetime.now().isoformat()
        })
        
        await message.answer(
            "Успешная авторизация."
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

@router.callback_query(F.data.startswith("check_"))
async def check_status_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    chat_id = callback.from_user.id

    status_data = await auth_client.check_login_status(login_token)    
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
        
        await delete_and_send(
            callback,
            "Успешная авторизация.\n"
            f"User ID: `{user_id}`"
        )
    
    elif status == 'expired':
        delete_user_state(chat_id)
        await delete_and_send(
            callback,
            "Токен устарел. Начните авторизацию заново: /login"
        )    
    elif status == 'denied':
        delete_user_state(chat_id)
        await delete_and_send(
            callback,
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