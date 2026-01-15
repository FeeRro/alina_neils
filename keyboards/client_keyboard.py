import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    
    if is_admin:
        builder.row(InlineKeyboardButton(text="👑 Админ-панель", callback_data="admin_panel"))
    
    builder.row(
        InlineKeyboardButton(text="✨ Записаться", callback_data="record"),
        InlineKeyboardButton(text="💅 Услуги", callback_data="services")
    )
    
    builder.row(
        InlineKeyboardButton(text="📍 Контакты", callback_data="contacts"),
        InlineKeyboardButton(text="🤗 Поддержка", callback_data="support")
    )
    
    return builder.as_markup()

def get_services_keyboard(services) -> InlineKeyboardMarkup:
    """Клавиатура с услугами"""
    builder = InlineKeyboardBuilder()
    
    for service in services:
        button_text = f"{service['name']} - {service['price']}₽"
        builder.row(InlineKeyboardButton(
            text=button_text,
            callback_data=f"service_{service['service_id']}"
        ))
    
    return builder.as_markup()

def get_dates_keyboard(dates) -> InlineKeyboardMarkup:
    """Клавиатура с датами"""
    builder = InlineKeyboardBuilder()
    
    for date_str in dates:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        day_name = get_weekday_name(date_obj.weekday())
        button_text = f"{date_obj.strftime('%d.%m')} ({day_name})"
        builder.button(
            text=button_text,
            callback_data=f"date_{date_str}"
        )
    
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_services"))
    
    return builder.as_markup()

def get_times_keyboard(times) -> InlineKeyboardMarkup:
    """Клавиатура со временем"""
    builder = InlineKeyboardBuilder()
    
    for time_str in times:
        builder.button(
            text=time_str,
            callback_data=f"time_{time_str}"
        )
    
    builder.adjust(3)
    return builder.as_markup()

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения записи"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking")
    )
    
    return builder.as_markup()

def get_weekday_name(weekday: int) -> str:
    """Получить название дня недели"""
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    return days[weekday]