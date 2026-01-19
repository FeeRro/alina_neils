# handlers/admin_handlers.py
from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.database import (
    is_admin, add_admin,  get_pending_bookings, update_booking_status,
    get_today_bookings, get_tomorrow_bookings, 
    get_statistics, get_clients_for_notification
)
from keyboards.admin_keyboard import (
    get_admin_main_keyboard, get_admin_booking_actions_keyboard,
    get_notification_groups_keyboard, get_reschedule_times_keyboard
)
from states.admin_states import AdminStates
from config import ADMIN_PASSWORD
import datetime

router = Router()

@router.message(Command("admin"))
async def admin_command_handler(message: Message, state: FSMContext):
    """Обработчик команды /admin"""
    # Если уже администратор
    if is_admin(message.from_user.id):
        await show_admin_panel(message)
        return
    
    # Запрашиваем пароль
    await message.answer("🔐 *Вход в админ-панель*\n\nВведите пароль:", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_password)

@router.message(AdminStates.waiting_password)
async def check_admin_password_handler(message: Message, state: FSMContext):
    """Проверка пароля администратора"""
    if message.text == ADMIN_PASSWORD:
        # Добавляем администратора
        add_admin(message.from_user.id)
        
        await message.answer("✅ *Доступ предоставлен!*", parse_mode="HTML")
        await show_admin_panel(message)
        await state.clear()
    else:
        await message.answer("❌ *Неверный пароль!*", parse_mode="HTML")

async def show_admin_panel(message: Message):
    """Показать админ-панель"""
    await message.answer(
        "👑 *Панель администратора*\n\nВыберите действие:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback_handler(callback: CallbackQuery):
    """Обработчик кнопки админ-панели"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    await callback.answer()
    await show_admin_panel(callback.message)

@router.callback_query(F.data == "admin_pending")
async def admin_pending_handler(callback: CallbackQuery):
    """Показать ожидающие записи"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    await callback.answer()
    
    bookings = get_pending_bookings()
    
    if not bookings:
        await callback.message.answer("✅ Нет записей, ожидающих подтверждения.")
        return
    
    for booking in bookings:
        text = (
            f"⏳ Запись #{booking['booking_id']}\n\n"
            f" № TG: @{booking['username']}\n"
            f"👤 Клиент: {booking['first_name']}\n"
            f"💅 Услуга: {booking['service_name']}\n"
            f"💰 Цена: {booking['price']}₽\n"
            f"📅 Дата: {booking['booking_datetime'][:10]}\n"
            f"⏰ Время: {booking['booking_datetime'][11:16]}\n"
        )
        
        await callback.message.answer(
            text,
            reply_markup=get_admin_booking_actions_keyboard(
                booking['booking_id'], 
                booking['user_id']
            ),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "admin_today")
async def admin_today_handler(callback: CallbackQuery):
    """Показать записи на сегодня"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    await callback.answer()
    
    bookings = get_today_bookings()
    
    if not bookings:
        await callback.message.answer("✅ Нет записей, на сегодня.")
        return
    
    for booking in bookings:
        text = (
            f"⏳ Запись #{booking['booking_id']}\n\n"
            f" № TG: @{booking['username']}\n"
            f"👤 Клиент: {booking['first_name']}\n"
            f"💅 Услуга: {booking['service_name']}\n"
            f"💰 Цена: {booking['price']}₽\n"
            f"📅 Дата: {booking['booking_datetime'][:10]}\n"
            f"⏰ Время: {booking['booking_datetime'][11:16]}\n"
        )
        
        await callback.message.answer(
            text,
            parse_mode="HTML"
        )

@router.callback_query(F.data == "admin_tomorrow")
async def admin_today_handler(callback: CallbackQuery):
    """Показать записи на завтра"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    await callback.answer()
    
    bookings = get_tomorrow_bookings()
    
    if not bookings:
        await callback.message.answer("✅ Нет записей, на завтра.")
        return
    
    for booking in bookings:
        text = (
            f"⏳ Запись #{booking['booking_id']}\n\n"
            f" № TG: @{booking['username']}\n"
            f"👤 Клиент: {booking['first_name']}\n"
            f"💅 Услуга: {booking['service_name']}\n"
            f"💰 Цена: {booking['price']}₽\n"
            f"📅 Дата: {booking['booking_datetime'][:10]}\n"
            f"⏰ Время: {booking['booking_datetime'][11:16]}\n"
        )
        
        await callback.message.answer(
            text,
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirm_handler(callback: CallbackQuery, bot):
    """Подтвердить запись"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    await callback.answer()
    
    booking_id = int(callback.data.split("_")[2])
    
    # Обновляем статус
    update_booking_status(booking_id, 'confirmed')
    
    # Уведомляем клиента
    from database.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.user_id, u.first_name, s.name, b.booking_datetime, s.duration_minutes, s.price
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE b.booking_id = ?
    ''', (booking_id,))
    
    booking = cursor.fetchone()
    conn.close()
    
    if booking:
        dt = datetime.datetime.strptime(booking['booking_datetime'], '%Y-%m-%d %H:%M:%S')
        end_time = dt + datetime.timedelta(minutes=booking['duration_minutes'])
        
        try:
            await bot.send_message(
                chat_id=booking['user_id'],
                text=f"🎉 Ваша запись подтверждена!\n\n"
                     f"💅 Услуга: {booking['name']}\n"
                     f"📅 Дата: {dt.strftime('%d.%m.%Y')}\n"
                     f"⏰ Время: {dt.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n"
                     f"💰 Стоимость: {booking['price']}₽\n\n"
                     f"👨‍🔧 Админ Федя: @Izera666\n"
                     f"💃🏼 Мастер Алина: @AlinaK_nail\n\n"
                     f"📍 Адрес: г. Москва, ул. Садовая Триумфальная, д. 4/10\n\n"
                     f"💖 Ждем вас!\n\n"
                     f" Чтобы переидти в главное меню: /start",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка уведомления клиента: {e}")
    
    await callback.message.answer(f"✅ Запись #{booking_id} подтверждена.\n главное меню админа: /admin")

@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_handler(callback: CallbackQuery, bot):
    """Отменить запись"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    await callback.answer()
    
    booking_id = int(callback.data.split("_")[2])
    
    # Обновляем статус
    update_booking_status(booking_id, 'cancelled')
    
    # Уведомляем клиента
    from database.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.user_id, u.first_name, s.name, b.booking_datetime, s.duration_minutes, s.price
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE b.booking_id = ?
    ''', (booking_id,))
    
    booking = cursor.fetchone()
    conn.close()
    
    if booking:
        dt = datetime.datetime.strptime(booking['booking_datetime'], '%Y-%m-%d %H:%M:%S')
        end_time = dt + datetime.timedelta(minutes=booking['duration_minutes'])
        
        try:
            await bot.send_message(
                chat_id=booking['user_id'],
                text=f"❌ Ваша запись отменена\n\n"
                     f"💅 Услуга: {booking['name']}\n"
                     f"📅 Дата: {dt.strftime('%d.%m.%Y')}\n"
                     f"⏰ Время: {dt.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n"
                     f"💰 Стоимость: {booking['price']}₽\n\n"
                     f"По вопросам обращайтесь:\n"
                     f"👨‍🔧 Админ Федя: @Izera666\n"
                     f"💃🏼 Мастер Алина: @AlinaK_nail\n\n"
                     f"Можете создать новую запись:\n"
                     f"Чтобы переидти в главное меню: /start",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка уведомления клиента: {e}")
    
    await callback.message.answer(f"❌ Запись #{booking_id} отменена.\nГлавное меню админа: /admin")

# ... (другие обработчики администратора)

