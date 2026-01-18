from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import jwt

from utils.redis_utils import set_user_state, get_user_state, delete_user_state
from utils.auth_client import auth_client
from utils.token_utils import make_authorized_request

router = Router()

async def delete_and_send(message_or_callback, text, **kwargs):
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.delete()
        return await message_or_callback.message.answer(text, **kwargs)
    else:
        return await message_or_callback.answer(text, **kwargs)


@router.message(Command("register"), ~F.text.contains(" "))
@router.message(Command("reg"), ~F.text.contains(" "))
async def reg_no_args(message: Message):
    await message.answer(
        "Использование команды:\n"
        "/register [email] [password]"
    )
@router.message(Command("register"))
@router.message(Command("reg"))
async def register_command(message: Message, command: CommandObject = None):    
    args = command.args.strip().split()
    if len(args) != 2:
        await message.answer(
            "Неверный формат. Использование: /register [email] [password]"
        )
        return
    
    email, password = args[0], args[1]
    
    await message.answer("Регистрирация пользователя...")
    
    result = await auth_client.register_user(email, password)
    
    if 'error' in result:
        await message.answer(f"Ошибка регистрации: {result['error']}")
        return
    
    if 'access_token' in result and 'refresh_token' in result:
        access_token = result['access_token']
        refresh_token = result['refresh_token']
        
        try:
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            user_id = decoded.get('user_id')
        except Exception:
            user_id = None
        
        set_user_state(message.chat.id, 'authorized', {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'email': email,
            'authorized_at': datetime.now().isoformat()
        })
        
        await message.answer(
            "Регистрация успешна!\n"
            f"Email: {email}\n"
            f"User ID: {user_id if user_id else 'N/A'}\n\n"
            "Вы авторизованы."
        )
    else:
        await message.answer("Регистрация выполнена, но не удалось получить токены.")

@router.message(Command("login"))
@router.message(Command("l"))
async def login_command(message: Message, command: CommandObject = None):
    chat_id = message.chat.id
    
    user_state = get_user_state(chat_id)
    
    if user_state['state'] == 'authorized':
        await message.answer("Вы уже авторизованы.")
        return
    
    if command and command.args:
        args = command.args.strip().split()
        if len(args) == 2:
            email, password = args[0], args[1]
            
            await message.answer("Выполняется вход...")
            
            result = await auth_client.login_user(email, password)
            
            if 'error' in result:
                await message.answer(f"Ошибка входа: {result['error']}")
                return
            
            if 'access_token' in result and 'refresh_token' in result:
                access_token = result['access_token']
                refresh_token = result['refresh_token']
                
                try:
                    decoded = jwt.decode(access_token, options={"verify_signature": False})
                    user_id = decoded.get('user_id')
                    id_result, id_error = await make_authorized_request(
                        message.chat.id, "GET", "/api/user_id"
                    )
                    numeric_id = None
                    if not id_error and isinstance(id_result, dict):
                        numeric_id = id_result.get('user_id')
                except Exception:
                    user_id = None
                    numeric_id = None
                
                set_user_state(chat_id, 'authorized', {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user_id': user_id,
                    'numeric_id': numeric_id,
                    'email': email,
                    'authorized_at': datetime.now().isoformat()
                })
                
                await message.answer(f"Вход выполнен!\nТеперь вы можете использовать команды для авторизованных пользователей. Подробнее: /help")
                return
            else:
                await message.answer("Ошибка: не получены токены")
                return

    result = await auth_client.create_login_token()
    
    if 'error' in result:
        await message.answer(f"Ошибка создания токена: {result['error']}")
        return
    
    login_token = result.get('login_token')
    
    if not login_token:
        await message.answer("Не удалось получить токен входа.")
        return
    
    set_user_state(chat_id, 'anonymous', {
        'login_token': login_token,
        'created_at': datetime.now().isoformat()
    })
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="GitHub", callback_data=f"github_{login_token}"),
            InlineKeyboardButton(text="Яндекс", callback_data=f"yandex_{login_token}")
        ],
        [
            InlineKeyboardButton(text="Код", callback_data=f"code_{login_token}")
        ]
    ])
    
    await message.answer(
        "Выберите способ авторизации:\n\n"
        "1. GitHub - авторизация через аккаунт GitHub\n"
        "2. Яндекс - авторизация через Яндекс ID\n"
        "3. Код - получить код для входа на другом устройстве",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("github_"))
async def github_login_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    
    auth_url = await auth_client.get_github_auth_url(login_token)
    
    if not auth_url:
        await callback.message.answer("Ошибка получения ссылки для GitHub авторизации.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Авторизация через GitHub", url=auth_url)],
        [InlineKeyboardButton(text="Проверить авторизацию", callback_data=f"check_{login_token}")]
    ])
    
    await delete_and_send(
        callback,
        "Авторизация через GitHub\n\n"
        "1. Нажмите на ссылку ниже\n"
        "2. Авторизуйтесь в GitHub\n"
        "3. После успешной авторизации вернитесь в бот и нажмите Проверить авторизацию\n\n"
        "У вас есть 1 минута на авторизацию",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("yandex_"))
async def yandex_login_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    
    auth_url = await auth_client.get_yandex_auth_url(login_token)
    
    if not auth_url:
        await callback.message.answer("Ошибка получения ссылки для Яндекс авторизации.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Авторизация через Яндекс", url=auth_url)],
        [InlineKeyboardButton(text="Проверить авторизацию", callback_data=f"check_{login_token}")]
    ])
    
    await delete_and_send(
        callback,
        "Авторизация через Яндекс\n\n"
        "1. Нажмите на ссылку ниже\n"
        "2. Авторизуйтесь в Яндекс ID\n"
        "3. После успешной авторизации вернитесь в бот и нажмите Проверить авторизацию\n\n"
        "У вас есть 1 минута на авторизацию",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("code_"))
async def code_login_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    
    result = await auth_client.get_code_for_login(login_token)
    
    if 'error' in result:
        await delete_and_send(callback, f"Ошибка получения кода: {result['error']}")
        return
    
    code = result.get('code')
    
    if not code:
        await delete_and_send(callback, "Не удалось получить код.")
        return
    
    await delete_and_send(
        callback,
        f"Ваш код для входа: {code}\n\n"
        "Код действителен 1 минуту.\n"
        "Введите его на другом устройстве, где вы уже авторизованы."
    )

@router.callback_query(F.data.startswith("check_"))
async def check_login_status_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    chat_id = callback.from_user.id
    
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'anonymous':
        await callback.message.answer("Неверное состояние пользователя.")
        return
    
    if user_state.get('login_token') != login_token:
        await callback.message.answer("Токен не совпадает.")
        return
    
    status_data = await auth_client.check_login_status(login_token)
    
    if 'error' in status_data:
        await callback.message.answer(f"Ошибка проверки статуса: {status_data['error']}")
        return
    
    status = status_data.get('status')
    
    if status in ['authorized', 'approved']:
        access_token = status_data.get('access_token')
        refresh_token = status_data.get('refresh_token')
        
        if not access_token or not refresh_token:
            await callback.message.answer("Ошибка: не получены токены доступа.")
            return
        
        try:
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            user_id = decoded.get('user_id')
            email = decoded.get('email')
            roles = decoded.get('roles', [])
            permissions = decoded.get('permissions', [])
        except Exception:
            user_id = None
            email = None
            roles = []
            permissions = []
        
        set_user_state(chat_id, 'authorized', {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'email': email,
            'roles': roles,
            'permissions': permissions,
            'authorized_at': datetime.now().isoformat()
        })
        
        response = "Авторизация успешно завершена!\n\n"
        if user_id:
            response += f"User ID: {user_id}\n"
        if email:
            response += f"Email: {email}\n"
        if roles:
            response += f"Роли: {', '.join(roles)}"
        
        await callback.message.answer(response)
    
    elif status == 'pending':
        await callback.message.answer("Авторизация еще не завершена. Пожалуйста, подождите.")
    
    elif status == 'denied':
        delete_user_state(chat_id)
        await callback.message.answer("Авторизация отклонена. Попробуйте снова: /login")
    
    else:
        await callback.message.answer(f"Неизвестный статус: {status}")

@router.message(Command("enter_code"))
async def enter_code_command(message: Message, command: CommandObject = None):
    if not command or not command.args:
        await message.answer("Использование: /enter_code [код]")
        return
    
    code = command.args.strip()
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Для ввода кода надо авторизоваться.")
        return
    
    refresh_token = user_state.get('refresh_token')
    
    if not refresh_token:
        await message.answer("Ошибка: нет refresh token. Начните авторизацию через GitHub/Яндекс для получения refresh token.")
        return
    
    result = await auth_client.verify_code_with_refresh_token(code, refresh_token)
    
    if 'error' in result:
        await message.answer(f"Ошибка: {result['error']}")
        return
    
    if result.get('status') == 'approved':
        await message.answer("Код успешно подтвержден! Теперь проверьте статус авторизации.")
    else:
        await message.answer("Неверный код или время действия истекло.")

@router.message(Command("my_permissions"))
async def my_permissions_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] != 'authorized':
        await message.answer("Сначала авторизуйтесь: /login")
        return
    
    access_token = user_state.get('access_token')
    
    try:
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        permissions = decoded.get('permissions', [])
        roles = decoded.get('roles', [])
        
        response = "Ваши права доступа:\n\n"
        response += f"Роли: {', '.join(roles) if roles else 'нет'}\n"
        response += f"Права ({len(permissions)}):\n"
        
        if permissions:
            for perm in permissions:
                response += f"  • {perm}\n"
        else:
            response += "  нет прав"
        
        await message.answer(response)
    except Exception as e:
        await message.answer(f"Ошибка получения прав: {e}")

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
    
    if 'error' in result:
        await message.answer(f"Ошибка обновления токенов: {result['error']}")
        return
    
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

@router.message(Command("debug"))
async def debug_command(message: Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    response = f"Статус: {user_state['state']}\n"
    
    if user_state['state'] == 'authorized':
        access_token = user_state.get('access_token', '')
        refresh_token = user_state.get('refresh_token', '')
        user_id = user_state.get('user_id', 'нет')
        
        response += f"User ID: {user_id}\n"
        response += f"Access token: {access_token[:30] if access_token else 'нет'}...\n"
        response += f"Refresh token: {refresh_token[:30] if refresh_token else 'нет'}...\n"
        
        if access_token:
            try:
                decoded = jwt.decode(access_token, options={"verify_signature": False})
                response += f"\nJWT payload:\n"
                for key, value in decoded.items():
                    response += f"  {key}: {value}\n"
            except Exception as e:
                response += f"\nОшибка декодирования JWT: {e}\n"
    
    await message.answer(response)