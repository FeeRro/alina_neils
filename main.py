from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import sqlite3
import config

bot = Bot(config.token)
dp = Dispatcher()


@dp.message(Command['start'])
async def start(message: Message):
    await message.answer("Привет!")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())