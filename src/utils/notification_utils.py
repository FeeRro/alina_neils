import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from database.database import get_db_connection
from config import TOKEN
from keyboards.admin_keyboard import get_admin_booking_actions_keyboard

async def send_daily_reminders():
    """Ежедневная отправка напоминаний"""
    bot = Bot(TOKEN)
    
    while True:
        try:
            # Находим записи на завтра
            tomorrow = datetime.now().date() + timedelta(days=1)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT b.user_id, u.first_name, s.name, b.booking_datetime, s.duration_minutes
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN services s ON b.service_id = s.service_id
                WHERE DATE(b.booking_datetime) = ? AND b.status = 'confirmed'
            ''', (tomorrow,))
            
            bookings = cursor.fetchall()
            conn.close()
            
            # Отправляем напоминания
            for booking in bookings:
                user_id, first_name, service_name, booking_datetime, duration = booking
                
                dt = datetime.strptime(booking_datetime, '%Y-%m-%d %H:%M:%S')
                end_time = dt + timedelta(minutes=duration)
                
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"🔔 *Напоминание о записи!*\n\n"
                             f"Завтра, {dt.strftime('%d.%m.%Y')}, у вас запись:\n"
                             f"💅 *{service_name}*\n"
                             f"⏰ *Время:* {dt.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n\n"
                             f"📍 *Адрес:* г. Москва, ул. Садовая Триумфальная, д. 4/10\n\n"
                             "💖 *Ждем вас!*",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Ошибка отправки напоминания: {e}")
                
                await asyncio.sleep(0.1)
            
            # Ждем до начала за 2 часа
            await asyncio.sleep(2 * 60 * 60)
            
        except Exception as e:
            print(f"Ошибка в daily_reminders: {e}")
            await asyncio.sleep(3600)
        finally:
            await bot.session.close()

async def notify_admins_about_new_booking(bot: Bot, booking_id: int, user_id: int, user_info: dict, 
                                         service_name: str, booking_datetime: str, 
                                         duration: int, price: int):
    """Уведомить администраторов о новой записи"""
    from database.database import get_all_admins
    
    admins = get_all_admins()
    
    dt = datetime.strptime(booking_datetime, '%Y-%m-%d %H:%M:%S')
    end_time = dt + timedelta(minutes=duration)
    
    message = (
        f"📥 Новая запись! #{booking_id}\n\n"
        f"👤 Клиент: {user_info['first_name']} "
        f"(@{user_info.get('username', 'нет username')})\n"
        f"💅 Услуга: {service_name}\n"
        f"💰 Цена: {price}₽\n"
        f"📅 Дата: {dt.strftime('%d.%m.%Y')}\n"
        f"⏰ Время: {dt.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n\n"        
    )

    
    for admin_id in admins:
        try:
            await bot.send_message(
                chat_id=admin_id,
                reply_markup=get_admin_booking_actions_keyboard(booking_id, user_id),
                text=message,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка уведомления администратора {admin_id}: {e}")