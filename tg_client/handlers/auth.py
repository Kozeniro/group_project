from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import jwt

from utils.redis_utils import set_user_state, get_user_state, delete_user_state
from utils.auth_client import auth_client

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
                except Exception:
                    user_id = None
                
                set_user_state(chat_id, 'authorized', {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user_id': user_id,
                    'email': email,
                    'authorized_at': datetime.now().isoformat()
                })
                
                await message.answer(f"Вход выполнен!\nUser ID: {user_id if user_id else 'N/A'}")
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
            InlineKeyboardButton(
                text="GitHub",
                callback_data=f"github_{login_token}"
            ),
            InlineKeyboardButton(
                text="Яндекс", 
                callback_data=f"yandex_{login_token}"
            )
        ]
    ])
    
    await message.answer(
        "Выберите способ входа:\n\n"
        "-Авторизация через GitHub\n"
        "-Авторизация через Яндекс ID",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("github_"))
async def github_login_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    chat_id = callback.from_user.id
    
    
    auth_url = await auth_client.get_github_auth_url(login_token)
    
    if not auth_url:
        await callback.message.answer("Ошибка получения ссылки для GitHub авторизации.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Авторизация через GitHub", 
            url=auth_url
        )],
        [InlineKeyboardButton(
            text="Проверить авторизацию", 
            callback_data=f"gh_finish_{login_token}"
        )]
    ])
    
    await delete_and_send(
        callback,
        "Авторизация через GitHub\n\n"
        "1. Нажмите на ссылку ниже\n"
        "2. Авторизуйтесь в GitHub\n"
        "3. После успешной авторизации вернитесь в бот и нажмите 'Проверить авторизацию'\n\n"
        "У вас есть 5 минут на авторизацию",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("gh_finish_"))
async def github_finish_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[2]
    chat_id = callback.from_user.id
    
    await callback.message.answer("Получение кода подтверждения...")
    
    
    code_result = await auth_client.get_code_for_token(login_token)
    
    if 'error' in code_result:
        await callback.message.answer(
            f"Не удалось получить код: {code_result['error']}\n\n"
            "Возможные причины:\n"
            "- Вы не авторизовались в GitHub\n"
            "- Токен устарел (прошло больше 5 минут)\n"
            "- Попробуйте снова: /login"
        )
        return
    
    code = code_result.get('code')
    if not code:
        await callback.message.answer("Не удалось получить код подтверждения.")
        return
    
    await callback.message.answer(f"Получен код: {code}\n\nПроверка кода...")
    
    
    verify_result = await auth_client.verify_code(code)
    
    if verify_result.get('success'):
        data = verify_result.get('data', {})
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        if not access_token or not refresh_token:
            await callback.message.answer("Ошибка: не получены токены")
            return
        
        
        try:
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            user_id = decoded.get('user_id')
            github_id = decoded.get('github_id')
            email = decoded.get('email')
            roles = decoded.get('roles', [])
            permissions = decoded.get('permissions', [])
        except Exception as e:
            user_id = None
            github_id = None
            email = None
            roles = []
            permissions = []
        
        
        set_user_state(chat_id, 'authorized', {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'github_id': github_id,
            'email': email,
            'roles': roles,
            'permissions': permissions,
            'authorized_at': datetime.now().isoformat()
        })
        
        
        response = "Авторизация через GitHub успешно завершена!\n\n"
        if user_id:
            response += f"User ID: {user_id}\n"
        if github_id:
            response += f"GitHub ID: {github_id}\n"
        if email:
            response += f"Email: {email}\n"
        if roles:
            response += f"Роли: {', '.join(roles)}\n"
        
        response += "\nТеперь вы можете использовать команды для авторизованных пользователей. Подробнее: /help"
        
        await callback.message.answer(response)
    else:
        error_msg = verify_result.get('error', 'Неизвестная ошибка')
        await callback.message.answer(
            f"Ошибка верификации кода: {error_msg}\n\n"
            "Попробуйте снова: /login"
        )

@router.callback_query(F.data.startswith("yandex_"))
async def yandex_login_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[1]
    
    auth_url = await auth_client.get_yandex_auth_url(login_token)
    
    if not auth_url:
        await callback.message.answer("Ошибка получения ссылки для Яндекс авторизации.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Авторизация через Яндекс", 
            url=auth_url
        )],
        [InlineKeyboardButton(
            text="Проверить авторизацию", 
            callback_data=f"ya_finish_{login_token}"
        )]
    ])
    
    await delete_and_send(
        callback,
        "Авторизация через Яндекс\n\n"
        "1. Нажмите на ссылку ниже\n"
        "2. Авторизуйтесь в Яндекс ID\n"
        "3. После успешной авторизации вернитесь в бот и нажмите 'Проверить авторизацию'\n\n"
        "У вас есть 5 минут на авторизацию",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("ya_finish_"))
async def yandex_finish_handler(callback: CallbackQuery):
    login_token = callback.data.split("_")[2]
    chat_id = callback.from_user.id
    
    await callback.message.answer("Получение кода подтверждения...")
    
    
    code_result = await auth_client.get_code_for_token(login_token)
    
    if 'error' in code_result:
        await callback.message.answer(
            f"Не удалось получить код: {code_result['error']}\n\n"
            "Возможные причины:\n"
            "- Вы не авторизовались в Яндекс\n"
            "- Токен устарел (прошло больше 5 минут)\n"
            "- Попробуйте снова: /login"
        )
        return
    
    code = code_result.get('code')
    if not code:
        await callback.message.answer("Не удалось получить код подтверждения.")
        return
    
    await callback.message.answer(f"Получен код: {code}\n\nПроверка кода...")
    
    
    verify_result = await auth_client.verify_code(code)
    
    if verify_result.get('success'):
        data = verify_result.get('data', {})
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        if not access_token or not refresh_token:
            await callback.message.answer("Ошибка: не получены токены")
            return
        
        
        try:
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            user_id = decoded.get('user_id')
            yandex_id = decoded.get('yandex_id')
            email = decoded.get('email')
            roles = decoded.get('roles', [])
            permissions = decoded.get('permissions', [])
        except Exception as e:
            user_id = None
            yandex_id = None
            email = None
            roles = []
            permissions = []
        
        
        set_user_state(chat_id, 'authorized', {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'yandex_id': yandex_id,
            'email': email,
            'roles': roles,
            'permissions': permissions,
            'authorized_at': datetime.now().isoformat()
        })
        
        
        response = "Авторизация через Яндекс успешно завершена!\n\n"
        if user_id:
            response += f"User ID: {user_id}\n"
        if yandex_id:
            response += f"Яндекс ID: {yandex_id}\n"
        if email:
            response += f"Email: {email}\n"
        if roles:
            response += f"Роли: {', '.join(roles)}\n"
        
        response += "\nТеперь вы можете использовать команды:\n"
        response += "/profile - ваш профиль\n"
        response += "/courses - список курсов\n"
        response += "/my_permissions - ваши права"
        
        await callback.message.answer(response)
    else:
        error_msg = verify_result.get('error', 'Неизвестная ошибка')
        await callback.message.answer(
            f"Ошибка верификации кода: {error_msg}\n\n"
            "Попробуйте снова: /login"
        )

@router.message(Command("enter_code"))
async def enter_code_command(message: Message, command: CommandObject = None):
    if not command or not command.args:
        await message.answer(
            "Использование: /enter_code [6-значный_код]\n\n"
            "Код вы получаете после авторизации через GitHub или Яндекс на другом устройстве."
        )
        return
    
    code = command.args.strip()
    
    if not code.isdigit() or len(code) != 6:
        await message.answer("Код должен состоять из 6 цифр")
        return
    
    await message.answer(f"Проверка кода: {code}")
    
    
    verify_result = await auth_client.verify_code(code)
    
    if verify_result.get('success'):
        data = verify_result.get('data', {})
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        if not access_token or not refresh_token:
            await message.answer("Ошибка: не получены токены")
            return
        
        try:
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            user_id = decoded.get('user_id')
            email = decoded.get('email')
            roles = decoded.get('roles', [])
        except Exception as e:
            user_id = None
            email = None
            roles = []
        
        
        set_user_state(message.chat.id, 'authorized', {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'email': email,
            'roles': roles,
            'authorized_at': datetime.now().isoformat()
        })
        
        response = "Вход по коду успешно выполнен!\n\n"
        if user_id:
            response += f"User ID: {user_id}\n"
        if email:
            response += f"Email: {email}\n"
        if roles:
            response += f"Роли: {', '.join(roles)}"
        
        await message.answer(response)
    else:
        error_msg = verify_result.get('error', 'Неизвестная ошибка')
        await message.answer(
            f"Ошибка: {error_msg}\n\n"
            "Возможные причины:\n"
            "- Код неверный\n"
            "- Код устарел (действителен 60 секунд)\n"
            "- Код уже был использован\n"
            "Попробуйте получить новый код на другом устройстве"
        )

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
