import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from database.database import init_db
from utils.schedule_utils import init_schedule
from utils.notification_utils import send_daily_reminders

# Импортируем обработчики
from handlers.common_handles import router as common_router
from handlers.client_handlers import router as client_router
from handlers.admin_handlers import router as admin_router


async def main():
    # Инициализация базы данных
    init_db()
    init_schedule(days_ahead=30)
    
    # Инициализация бота
    bot = Bot(token=config.TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация роутеров
    dp.include_router(common_router)
    dp.include_router(client_router)
    dp.include_router(admin_router)

    
    # Запуск фоновых задач
    asyncio.create_task(send_daily_reminders())
    
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())