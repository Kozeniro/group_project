from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я Telegram-бот для группового проекта. Список команд: /help")

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("""
Доступные команды:
/start - начать работу
/help - помощь
/sum - сложить числа (/sum 1 2 3)

Напиши любое сообщение, и я его повтрю!
    """)

@dp.message(Command("sum"))
async def sum_handler(message: types.Message):
    text = message.text.replace("/sum", "").strip()
    
    if not text:
        await message.answer("Напиши числа! Пример: /sum 1 2 3")
        return
    numbers = []
    parts = text.split()
    total = 0
    
    for part in parts:
        num = int(part.strip())
        numbers.append(num)
        total += num

    await message.answer(str(total))

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Ваш текст: {message.text}")

async def main():
    print(">>>Бот запущен<<<")
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())