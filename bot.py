import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from db import Database
from handlers import register_handlers

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

db = Database(DB_USER, DB_PASS, DB_NAME, DB_HOST, DB_PORT)
bot.db = db

async def main():
    await db.create_tables()

    # ✅ Робимо базу доступною у всіх handler’ах
    dp['db'] = db

    # ✅ Реєструємо всі команди / callback-и
    register_handlers(dp, db)

    print("🤖 FinanceBot запущено.")
    import asyncio

    print("⏳ Waiting 5 seconds before polling...")
    await asyncio.sleep(5)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
