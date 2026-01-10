from aiogram import Bot, Dispatcher
import asyncio
from utils.config import Config
from handlers import routers

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

for router in routers:
    dp.include_router(router)

async def main():
    print(">>>Бот запущен<<<")
    await dp.start_polling(bot)    

if __name__ == "__main__":
    asyncio.run(main())