from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import logging
from middleware import AuthMiddleware

from utils.config import Config
from handlers import routers
from periodic_tasks import PeriodicTasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=Config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
for router in routers:
    dp.include_router(router)
dp.message.middleware(AuthMiddleware())

async def main():
    periodic_tasks = PeriodicTasks(bot)
    await periodic_tasks.start()
    
    print(">>>Бот запущен<<<")
    try:
        await dp.start_polling(bot)
    finally:
        await periodic_tasks.stop()

if __name__ == "__main__":
    asyncio.run(main())