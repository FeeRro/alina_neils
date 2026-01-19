import asyncio
import json
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from contextlib import asynccontextmanager

import config as config
from database.database import init_db
from utils.schedule_utils import init_schedule
from utils.notification_utils import send_daily_reminders

# Импортируем обработчики
from handlers.common_handles import router as common_router
from handlers.client_handlers import router as client_router
from handlers.admin_handlers import router as admin_router

# Глобальные переменные (для serverless)
bot = None
dp = None

async def init_bot():
    """Инициализация бота и диспетчера"""
    global bot, dp
    
    if bot is None or dp is None:
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
    
    return bot, dp

async def handler(event: dict, context):
    """Обработчик для serverless (Yandex Cloud Functions/AWS Lambda)"""
    body: str = event.get("body", "")
    update_data = json.loads(body) if body else {}
    
    # Инициализируем бота и диспетчер
    bot, dp = await init_bot()
    
    # Обрабатываем обновление
    await dp.feed_update(bot, Update.model_validate(update_data))
    
    return {"statusCode": 200, "body": ""}

async def polling_main():
    """Основная функция для запуска бота в режиме поллинга"""
    bot, dp = await init_bot()
    
    # Запуск фоновых задач (только для поллинга)
    asyncio.create_task(send_daily_reminders())
    
    print("✅ Бот запущен в режиме поллинга!")
    await dp.start_polling(bot)

async def webhook_main(webhook_url: str):
    """Основная функция для запуска бота в режиме вебхука"""
    bot, dp = await init_bot()
    
    # Устанавливаем вебхук
    await bot.set_webhook(webhook_url)
    
    print(f"✅ Бот запущен в режиме вебхука! Webhook URL: {webhook_url}")
    
    # Здесь обычно запускается веб-сервер (FastAPI, aiohttp и т.д.)
    # Для примера оставим ожидание
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # Выберите режим запуска
    MODE = "polling"  # или "webhook"
    
    if MODE == "polling":
        asyncio.run(polling_main())
    elif MODE == "webhook":
        # Укажите ваш вебхук URL
        WEBHOOK_URL = "https://functions.yandexcloud.net/d4el2lv6qf0mpiscgfj1"
        asyncio.run(webhook_main(WEBHOOK_URL))