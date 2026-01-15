from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 Ожидающие", callback_data="admin_pending"),
        InlineKeyboardButton(text="📅 Сегодня", callback_data="admin_today")
    )
    
    builder.row(
        InlineKeyboardButton(text="📆 Завтра", callback_data="admin_tomorrow"),
        InlineKeyboardButton(text="👥 Клиенты", callback_data="admin_clients")
    )
    
    builder.row(
        InlineKeyboardButton(text="📢 Уведомления", callback_data="admin_notify"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
    )
    
    builder.row(InlineKeyboardButton(text="🏠 Главная", callback_data="back_to_start"))
    
    return builder.as_markup()

def get_admin_booking_actions_keyboard(booking_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Действия с записью для администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{booking_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{booking_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔄 Перенести", callback_data=f"admin_reschedule_{booking_id}"),
        InlineKeyboardButton(text="📞 Связаться", url=f"tg://user?id={user_id}")
    )
    
    return builder.as_markup()

def get_notification_groups_keyboard() -> InlineKeyboardMarkup:
    """Группы для уведомлений"""
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="📢 Всем клиентам", callback_data="notify_all"))
    builder.row(InlineKeyboardButton(text="📅 На сегодня", callback_data="notify_today"))
    builder.row(InlineKeyboardButton(text="📆 На завтра", callback_data="notify_tomorrow"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel"))
    
    return builder.as_markup()

def get_reschedule_times_keyboard(times, booking_id: int, date_str: str) -> InlineKeyboardMarkup:
    """Время для переноса записи"""
    builder = InlineKeyboardBuilder()
    
    for time_str in times:
        builder.button(
            text=time_str,
            callback_data=f"reschedule_time_{booking_id}_{date_str}_{time_str}"
        )
    
    builder.adjust(3)
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_reschedule"))
    
    return builder.as_markup()