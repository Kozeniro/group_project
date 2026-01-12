from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import sys
from utils.config import Config
from handlers import routers


bot = Bot(
    token=Config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

for router in routers:
    dp.include_router(router)

async def main():
    print(">>>Бот запущен<<<")
    await dp.start_polling(bot)    

if __name__ == "__main__":
    asyncio.run(main())