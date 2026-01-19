# handlers/common_handlers.py
from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.client_keyboard import (
    get_main_menu_keyboard, get_back_to_start_keyboard
    )

router = Router()

@router.callback_query(F.data == "services")
async def services_handler(callback: CallbackQuery):
    """Показать услуги"""
    await callback.answer()
    
    services_text = (
        "💅 Выбери, чего не хаватает чтобы стать безупречной:\n\n"
        "1. Дизайн ногтей - 150₽ (10 мин)\n"
        "2. Комбинированный маникюр - 1500₽ (45 мин)\n"
        "3. Мужской маникюр - 2000₽ (1 час)\n"
        "4. Маникюр с покрытием гель-лаком - от 5000₽ (2 часа)\n"
        "5. Наращивание ногтей - 7500₽ (3-4 часа)\n"
        "6. Японский маникюр - 2500₽ (1 час)\n"
        "7. Педикюр с покрытием гель-лаком - 5000₽ (2часа)\n"
        "8. Снятие гель-лака - 1000₽ (30 мин)\n"
        "9. Обработка сложного участка - 1500₽ (20 мин)\n"
        "10. Маникюр с покрытием гелем - 4000₽ (2 час)\n\n"
        "💖 Каждая услуга выполняется с любовью и профессионализмом!"
    )
    
    await callback.message.answer(services_text, reply_markup=get_back_to_start_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "contacts")
async def contacts_handler(callback: CallbackQuery):
    """Показать контакты"""
    await callback.answer()
    
    contacts_text = (
        "📍 *Контакты и адрес:*\n\n"
        "🏠 *Адрес:*\n"
        "г. Москва, ул. Садовая Триумфальная, д. 4/10\n\n"
        "👩 *Мастер:*\n"
        "@AlinaK_nail\n\n"
        "⏰ *Часы работы:*\n"
        "Пн-Пт: 10:00 - 20:00\n"
        "Сб-Вс: 11:00 - 19:00\n"
        "Вернутся в меню: /start"
    )
    
    await callback.message.answer(contacts_text, reply_markup=get_back_to_start_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery):
    """Показать поддержку"""
    await callback.answer()
    
    support_text = (
        "🤗 Поддержка:\n\n"
        "👩 Мастер маникюра:\n"
        "@AlinaK_nail\n\n"
        "👨‍🔧 Админ:\n"
        "@Izera666\n\n"
        "🤖 Заказать тг бота:\n"
        "@prostodanyl\n\n"
        "*По всем вопросам обращайтесь к нам!\n"
    )
    
    await callback.message.answer(support_text, reply_markup=get_back_to_start_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "back_to_start")
async def back_to_start_handler(callback: CallbackQuery):
    """Вернуться в начало"""
    await callback.answer()
    
    # Отправляем приветствие
    await callback.message.answer(
        "Приветик, прелесть! 💕\n"
        "Как же я рад снова тебя видеть! Приготовься, сейчас мы быстренько и весело организуем запись.\n" 
        "И да, наш договор — только между нами! 🤝🌸",
        reply_markup=get_main_menu_keyboard(False), parse_mode="HTML"
    )
