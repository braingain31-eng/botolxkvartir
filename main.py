import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from handlers import start, search, payment, agent, errors
from database.firebase_db import init_firebase
from utils.scheduler import start_scheduler
from handlers.property import router as property_router
import config
import os

os.makedirs("temp", exist_ok=True)

logging.basicConfig(level=logging.INFO)
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def main():
    init_firebase()
    await start_scheduler()
    
    dp.include_router(start.router)
    dp.include_router(search.router)
    dp.include_router(payment.router)
    dp.include_router(agent.router)
    dp.include_router(errors.router)
    dp.include_router(property_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())