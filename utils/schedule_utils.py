import datetime
from typing import List
from database.database import get_db_connection
import config

def init_schedule(days_ahead: int = 60):
    """Инициализировать расписание на N дней вперед"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.date.today()
    
    for day in range(days_ahead):
        current_date = today + datetime.timedelta(days=day)
        
        # Определяем рабочие часы
        if current_date.weekday() == 4 or current_date.weekday() == 5 or current_date.weekday() == 3:  # Выходные
            continue
        elif current_date.weekday() == 6:  # Воскресенье
            work_hours = config.WORKING_HOURS_WEEKEND
        else:  # Будни
            work_hours = config.WORKING_HOURS_WEEKDAY
        
        for time in work_hours:
            cursor.execute('''
                INSERT OR IGNORE INTO schedule_slots (slot_date, slot_time) 
                VALUES (?, ?)
            ''', (current_date, time))
    
    conn.commit()
    conn.close()

def get_available_time_slots(date_str: str, service_duration: int) -> List[str]:
    """Получить доступные временные слоты"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем все слоты на дату
    cursor.execute('''
        SELECT slot_time, is_available 
        FROM schedule_slots 
        WHERE slot_date = ? 
        ORDER BY slot_time
    ''', (date_str,))
    
    slots = cursor.fetchall()
    
    # Получаем занятые записи
    cursor.execute('''
        SELECT b.booking_datetime, s.duration_minutes
        FROM bookings b
        JOIN services s ON b.service_id = s.service_id
        WHERE DATE(b.booking_datetime) = ? 
        AND b.status IN ('confirmed', 'pending')
    ''', (date_str,))
    
    bookings = cursor.fetchall()
    conn.close()
    
    # Создаем множество занятых слотов
    busy_slots = set()
    
    for booking_datetime, duration in bookings:
        start_time = datetime.datetime.strptime(booking_datetime, '%Y-%m-%d %H:%M:%S').time()
        
        # Вычисляем занятые слоты
        slots_needed = duration // 30
        if duration % 30 > 0:
            slots_needed += 1
        
        current_time = start_time
        for _ in range(slots_needed):
            busy_slots.add(current_time.strftime('%H:%M'))
            current_time = (datetime.datetime.combine(datetime.date.today(), current_time) + 
                          datetime.timedelta(minutes=30)).time()
    
    # Определяем доступные слоты для услуги
    available_slots = []
    slots_needed_for_service = service_duration // 30
    if service_duration % 30 > 0:
        slots_needed_for_service += 1

    now = datetime.datetime.now()
    current_date = now.date()
    slot_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    
    for i in range(len(slots) - slots_needed_for_service + 1):
        slot_time_str, is_available = slots[i]
        
        # Проверяем, свободен ли начальный слот
        if is_available and slot_time_str not in busy_slots:
            # Проверяем, свободны ли все последующие слоты
            all_free = True
            for j in range(slots_needed_for_service):
                next_slot_time, next_available = slots[i + j]
                if not next_available or next_slot_time in busy_slots:
                    all_free = False
                    break
            
            if all_free:
                # Проверяем, не прошло ли уже время слота
                slot_time = datetime.datetime.strptime(slot_time_str, "%H:%M").time()
                slot_datetime = datetime.datetime.combine(slot_date, slot_time)
                
                # Добавляем буфер (30 минут) для возможности записи
                buffer_time = datetime.timedelta(minutes=30)
                
                # Если дата в будущем или сегодня, но время еще не наступило (с учетом буфера)
                if slot_date > current_date or (slot_date == current_date and slot_datetime >= (now + buffer_time)):
                    available_slots.append(slot_time_str)
    
    return available_slots

def get_available_dates_with_slots(service_duration: int, days_ahead: int = 14) -> List[str]:
    """Получить даты с доступными слотами"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=days_ahead)
    
    cursor.execute('''
        SELECT DISTINCT slot_date 
        FROM schedule_slots 
        WHERE slot_date BETWEEN ? AND ?
        AND (CAST(strftime('%w', slot_date) AS INTEGER) NOT IN (4, 5, 6))
        ORDER BY slot_date
    ''', (today, end_date))
    
    all_dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Фильтруем даты
    available_dates = []
    for date_str in all_dates:
        if get_available_time_slots(date_str, service_duration):
            available_dates.append(date_str)
    
    return available_dates