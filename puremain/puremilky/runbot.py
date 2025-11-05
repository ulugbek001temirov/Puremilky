import asyncio
from app.database import init_db
from aiogram import Bot, Dispatcher,F
from aiogram.types import Message
from aiogram.filters import Command, Command 
from app.handlers import router
from dotenv import load_dotenv
import os
# from app.database.models import async_main

async def main():
    # await async_main()
    load_dotenv()
    init_db()
    TOKEN=os.getenv("TELEGRAM_TOKEN")
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    print(TOKEN)
    dp.include_router(router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")