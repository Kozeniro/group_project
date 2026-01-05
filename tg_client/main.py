from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

user_states = {}

def get_user_state(chat_id):
    return user_states.get(chat_id, {'state': 'unknown'})

def set_user_state(chat_id, state, data=None):
    if data is None:
        data = {}
    user_states[chat_id] = {'state': state, **data}

def delete_user_state(chat_id):
    if chat_id in user_states:
        del user_states[chat_id]


@dp.message(Command("start"))
async def start_command(message: types.Message):
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
    print(user_states)


@dp.message(Command("help"))
async def help_command(message: types.Message):
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


@dp.message(Command("status"))
async def status_command(message: types.Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)

    if user_state['state'] == 'unknown':
        await message.answer(f"Ваш статус: Неизвестный")
    elif user_state['state'] == 'anonymous':
        await message.answer(f"Ваш статус: Анонимный")
    else:
        await message.answer(f"Ваш статус: Авторизованный") 


@dp.message(Command("login"))
async def login_command(message: types.Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)
    
    if user_state['state'] == 'unknown':
        await message.answer("Сначала напиши /start")    
    elif user_state['state'] == 'authorized':
        await message.answer("Ты уже авторизован! Используй /logout для выхода")
    else: 
        await message.answer(
            "Начало авторизации\n"
            "Перейдите по ссылке:\n"
            "github.com/login/oauth/authorize\n"
            "Подтвердите вход и вернитесь в бота."
        )
        await message.answer("Вы авторизованы")
        set_user_state(chat_id, 'authorized')


@dp.message(Command("logout"))
async def status_command(message: types.Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)

    if user_state['state'] == 'unknown':
        await message.answer("Вы не авторизованы.")
    else:
        delete_user_state(chat_id)
        await message.answer("Сеанс завершён.") 
    

@dp.message(Command("tests"))
async def status_command(message: types.Message):
    chat_id = message.chat.id
    user_state = get_user_state(chat_id)

    if user_state['state'] != 'authorized':
        await message.answer("Вы не авторизованы.")
    else:
        await message.answer("Доступные тесты: [потом будет]") 
    

@dp.message()
async def echo(message: types.Message):
    await message.answer("Нет такой команды.")

async def main():
    print(">>>Бот запущен<<<")
    await dp.start_polling(bot)    

if __name__ == "__main__":
    asyncio.run(main())