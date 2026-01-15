import datetime
from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.database import (
    save_user, get_services, create_booking, get_user_bookings
)
from keyboards.client_keyboard import (
    get_main_menu_keyboard, get_services_keyboard,
    get_dates_keyboard, get_times_keyboard, get_confirmation_keyboard
)
from states.booking_states import BookingStates
from utils.schedule_utils import get_available_dates_with_slots, get_available_time_slots
from utils.notification_utils import notify_admins_about_new_booking
from utils.helpers import calculate_end_time

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    """Обработчик команды /start"""
    # Сохраняем пользователя
    save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Проверяем, администратор ли
    from database.database import is_admin
    admin = is_admin(message.from_user.id)
    
    # Отправляем приветствие
    await message.answer(
        "Привет, красотуля! 💖\n"
        "Я бот-ассистент. Я здесь, чтобы твои ручки стали безупречными, "
        "а запись - быстрой и простой!",
        reply_markup=get_main_menu_keyboard(is_admin=admin)
    )

@router.message(Command("my_bookings"))
async def my_bookings_handler(message: Message):
    """Показать мои записи"""
    bookings = get_user_bookings(message.from_user.id)
    
    if not bookings:
        await message.answer("У вас пока нет активных записей.")
        return
    
    text = "📋 *Ваши записи:*\n\n"
    
    for booking in bookings:
        status_emoji = "✅" if booking['status'] == 'confirmed' else "⏳" if booking['status'] == 'pending' else "❌"
        
        dt = datetime.datetime.strptime(booking['booking_datetime'], '%Y-%m-%d %H:%M:%S')
        
        text += (
            f"{status_emoji} *{booking['name']}*\n"
            f"📅 {dt.strftime('%d.%m.%Y')} ⏰ {dt.strftime('%H:%M')}\n"
            f"💰 {booking['price']}₽ | ID: {booking['booking_id']}\n\n"
        )
    
    await message.answer(text, parse_mode="Markdown")

@router.callback_query(F.data == "record")
async def record_handler(callback: CallbackQuery, state: FSMContext):
    """Начать процесс записи"""
    await callback.answer()
    
    services = get_services()
    await callback.message.answer(
        "💅 *Выберите услугу:*",
        reply_markup=get_services_keyboard(services),
        parse_mode="Markdown"
    )
    
    await state.set_state(BookingStates.selecting_service)

@router.callback_query(F.data.startswith("service_"), BookingStates.selecting_service)
async def select_service_handler(callback: CallbackQuery, state: FSMContext):
    """Выбрать услугу"""
    await callback.answer()
    
    service_id = int(callback.data.split("_")[1])
    
    from database.database import get_service_by_id
    service = get_service_by_id(service_id)
    
    if not service:
        await callback.message.answer("Услуга не найдена")
        return
    
    # Сохраняем данные
    await state.update_data(
        service_id=service_id,
        service_name=service['name'],
        service_price=service['price'],
        service_duration=service['duration_minutes']
    )
    
    # Получаем доступные даты
    available_dates = get_available_dates_with_slots(service['duration_minutes'])
    
    if not available_dates:
        await callback.message.answer(
            "😔 На ближайшие две недели нет свободных дат для этой услуги."
        )
        await state.clear()
        return
    
    await callback.message.answer(
        f"✨ *Вы выбрали:* {service['name']}\n"
        f"💰 *Цена:* {service['price']}₽\n"
        f"⏱ *Длительность:* {service['duration_minutes']} мин\n\n"
        "📅 *Выберите дату:*",
        reply_markup=get_dates_keyboard(available_dates),
        parse_mode="Markdown"
    )
    
    await state.set_state(BookingStates.selecting_date)

@router.callback_query(F.data.startswith("date_"), BookingStates.selecting_date)
async def select_date_handler(callback: CallbackQuery, state: FSMContext):
    """Выбрать дату"""
    await callback.answer()
    
    date_str = callback.data.split("_")[1]
    
    # Сохраняем дату
    await state.update_data(selected_date=date_str)
    
    # Получаем данные об услуге
    data = await state.get_data()
    duration = data.get('service_duration', 60)
    
    # Получаем доступное время
    available_times = get_available_time_slots(date_str, duration)
    
    if not available_times:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        await callback.message.answer(
            f"На {date_obj.strftime('%d.%m.%Y')} нет свободного времени."
        )
        return
    
    await callback.message.answer(
        "⏰ *Выберите время:*",
        reply_markup=get_times_keyboard(available_times),
        parse_mode="Markdown"
    )
    
    await state.set_state(BookingStates.selecting_time)

@router.callback_query(F.data.startswith("time_"), BookingStates.selecting_time)
async def select_time_handler(callback: CallbackQuery, state: FSMContext):
    """Выбрать время"""
    await callback.answer()
    
    time_str = callback.data.split("_")[1]
    
    # Получаем данные
    data = await state.get_data()
    service_name = data.get('service_name')
    service_price = data.get('service_price')
    service_duration = data.get('service_duration')
    selected_date = data.get('selected_date')
    
    # Формируем дату и время
    booking_datetime = f"{selected_date} {time_str}:00"
    dt = datetime.datetime.strptime(booking_datetime, '%Y-%m-%d %H:%M:%S')
    end_time = calculate_end_time(booking_datetime, service_duration)
    
    await callback.message.answer(
        f"📋 *Подтверждение записи:*\n\n"
        f"💅 *Услуга:* {service_name}\n"
        f"💰 *Цена:* {service_price}₽\n"
        f"⏱ *Длительность:* {service_duration} мин\n"
        f"📅 *Дата:* {dt.strftime('%d.%m.%Y')}\n"
        f"⏰ *Время:* {dt.strftime('%H:%M')} - {end_time}\n\n"
        "Подтверждаете запись?",
        reply_markup=get_confirmation_keyboard(),
        parse_mode="Markdown"
    )
    
    # Сохраняем время
    await state.update_data(
        selected_time=time_str,
        booking_datetime=booking_datetime
    )
    
    await state.set_state(BookingStates.confirming)

@router.callback_query(F.data == "confirm_booking", BookingStates.confirming)
async def confirm_booking_handler(callback: CallbackQuery, state: FSMContext, bot):
    """Подтвердить запись"""
    await callback.answer()
    
    # Получаем данные
    data = await state.get_data()
    user_id = callback.from_user.id
    service_id = data.get('service_id')
    service_name = data.get('service_name')
    service_price = data.get('service_price')
    service_duration = data.get('service_duration')
    booking_datetime = data.get('booking_datetime')
    
    # Создаем запись
    success, message, booking_id = create_booking(user_id, service_id, booking_datetime)
    
    if success:
        # Уведомляем администраторов
        user_info = {
            'first_name': callback.from_user.first_name,
            'username': callback.from_user.username
        }
        
        await notify_admins_about_new_booking(
            bot, booking_id, user_info, service_name, 
            booking_datetime, service_duration, service_price
        )
        
        # Формируем ответ
        dt = datetime.datetime.strptime(booking_datetime, '%Y-%m-%d %H:%M:%S')
        end_time = calculate_end_time(booking_datetime, service_duration)
        
        await callback.message.answer(
            f"🎉 *Запись успешно оформлена!* #{booking_id}\n\n"
            f"💅 *Услуга:* {service_name}\n"
            f"💰 *Цена:* {service_price}₽\n"
            f"📅 *Дата:* {dt.strftime('%d.%m.%Y')}\n"
            f"⏰ *Время:* {dt.strftime('%H:%M')} - {end_time}\n\n"
            "⏳ *Статус:* Ожидает подтверждения\n\n"
            "💖 *Ждем вас в салоне!*",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer(
            f"😔 *Ошибка:* {message}",
            parse_mode="Markdown"
        )
    
    await state.clear()

@router.callback_query(F.data == "cancel_booking")
async def cancel_booking_handler(callback: CallbackQuery, state: FSMContext):
    """Отменить запись"""
    await callback.answer("Запись отменена")
    await state.clear()
    await callback.message.answer("Запись отменена. Для новой записи нажмите /start")