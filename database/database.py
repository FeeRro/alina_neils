import sqlite3
import datetime
from typing import List, Tuple, Optional

def get_db_connection(db_name: str = 'users_id') -> sqlite3.Connection:
    """Создать соединение с базой данных"""
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица услуг
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            duration_minutes INTEGER NOT NULL,
            description TEXT
        )
    ''')

    # Таблица записей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings(
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            booking_datetime DATETIME NOT NULL,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (service_id) REFERENCES services (service_id)
        )          
    ''')

    # Таблица расписания
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_slots (
            slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_date DATE NOT NULL,
            slot_time TIME NOT NULL,
            is_available BOOLEAN DEFAULT 1,
            booking_id INTEGER,
            UNIQUE(slot_date, slot_time)
        )
    ''')

    # Таблица администраторов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Заполняем услуги
    default_services = [
        ('Дизайн ногтей', 150, 15, 'Создание уникального дизайна'),
        ('Комбинированный маникюр', 1500, 45, 'Комбинированная обработка кутикулы'),
        ('Мужской маникюр', 2000, 60, 'Уход за мужскими руками'),
        ('Маникюр с покрытием гель-лаком', 5000, 120, 'Маникюр с гель-лаком'),
        ('Наращивание ногтей', 7500, 180, 'Удлинение ногтевой пластины'),
        ('Японский маникюр', 2500, 60, 'Японская технология ухода'),
        ('Педикюр с покрытием гель-лаком', 5000, 120, 'Уход за стопами'),
        ('Снятие гель-лака', 1000, 30, 'Аккуратное снятие покрытия'),
        ('Обработка сложного участка', 1500, 20, 'Решение проблемных зон'),
        ('Маникюр с покрытием гелем', 4000, 120, 'Укрепление гелем')
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO services (name, price, duration_minutes, description) VALUES (?, ?, ?, ?)',
        default_services
    )
    
    conn.commit()
    conn.close()

# Функции для пользователей
def save_user(user_id: int, username: str, first_name: str, last_name: str = None):
    """Сохранить/обновить пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_activity) 
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()

def get_user(user_id: int):
    """Получить пользователя по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Функции для услуг
def get_services() -> List[sqlite3.Row]:
    """Получить все услуги"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services ORDER BY price')
    services = cursor.fetchall()
    conn.close()
    return services

def get_service_by_id(service_id: int):
    """Получить услугу по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services WHERE service_id = ?', (service_id,))
    service = cursor.fetchone()
    conn.close()
    return service

# Функции для записей
def create_booking(user_id: int, service_id: int, booking_datetime: str) -> Tuple[bool, str, int]:
    """Создать новую запись"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO bookings (user_id, service_id, booking_datetime, status)
            VALUES (?, ?, ?, 'pending')
        ''', (user_id, service_id, booking_datetime))
        
        booking_id = cursor.lastrowid
        conn.commit()
        return True, "Запись создана", booking_id
    except Exception as e:
        conn.rollback()
        return False, f"Ошибка: {str(e)}", 0
    finally:
        conn.close()

def get_user_bookings(user_id: int):
    """Получить записи пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.*, s.name, s.price 
        FROM bookings b
        JOIN services s ON b.service_id = s.service_id
        WHERE b.user_id = ?
        ORDER BY b.booking_datetime DESC
    ''', (user_id,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def update_booking_status(booking_id: int, status: str):
    """Обновить статус записи"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE bookings SET status = ? WHERE booking_id = ?', (status, booking_id))
    conn.commit()
    conn.close()

# Функции для администраторов
def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM admins WHERE user_id = ?', (user_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result

def add_admin(user_id: int):
    """Добавить администратора"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_admins():
    """Получить всех администраторов"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM admins')
    admins = [row[0] for row in cursor.fetchall()]
    conn.close()
    return admins

# Функции для статистики
def get_statistics():
    """Получить статистику"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Подтвержденные записи
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'confirmed'")
    stats['confirmed'] = cursor.fetchone()[0]
    
    # Ожидающие подтверждения
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
    stats['pending'] = cursor.fetchone()[0]
    
    # Записи на сегодня
    today = datetime.date.today()
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE DATE(booking_datetime) = ? AND status = 'confirmed'", (today,))
    stats['today'] = cursor.fetchone()[0]
    
    # Общая выручка
    cursor.execute("SELECT SUM(s.price) FROM bookings b JOIN services s ON b.service_id = s.service_id WHERE b.status = 'confirmed'")
    stats['revenue'] = cursor.fetchone()[0] or 0
    
    # Уникальные клиенты
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM bookings")
    stats['unique_clients'] = cursor.fetchone()[0]
    
    # Всего пользователей
    cursor.execute("SELECT COUNT(*) FROM users")
    stats['total_users'] = cursor.fetchone()[0]
    
    conn.close()
    return stats

# Функции для уведомлений
def get_clients_for_notification(group: str = 'all'):
    """Получить клиентов для уведомления"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if group == 'today':
        today = datetime.date.today()
        cursor.execute('''
            SELECT DISTINCT b.user_id 
            FROM bookings b
            WHERE DATE(b.booking_datetime) = ? AND b.status = 'confirmed'
        ''', (today,))
    elif group == 'tomorrow':
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        cursor.execute('''
            SELECT DISTINCT b.user_id 
            FROM bookings b
            WHERE DATE(b.booking_datetime) = ? AND b.status = 'confirmed'
        ''', (tomorrow,))
    else:  # all
        cursor.execute("SELECT DISTINCT user_id FROM bookings WHERE user_id IS NOT NULL")
    
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients


# Функции для работы с записями администратора
def get_pending_bookings():
    """Получить все записи, ожидающие подтверждения"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE b.status = 'pending'
        ORDER BY b.booking_datetime ASC
    ''')
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_today_bookings():
    """Получить подтвержденные записи на сегодня"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.date.today()
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE DATE(b.booking_datetime) = ? 
        AND b.status = 'confirmed'
        ORDER BY b.booking_datetime ASC
    ''', (today,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_tomorrow_bookings():
    """Получить подтвержденные записи на завтра"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE DATE(b.booking_datetime) = ? 
        AND b.status = 'confirmed'
        ORDER BY b.booking_datetime ASC
    ''', (tomorrow,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_booking_by_id(booking_id: int):
    """Получить запись по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.*,
            u.first_name,
            u.username,
            u.phone,
            s.name as service_name,
            s.price,
            s.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE b.booking_id = ?
    ''', (booking_id,))
    
    booking = cursor.fetchone()
    conn.close()
    return booking

def get_week_bookings():
    """Получить записи на текущую неделю"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE DATE(b.booking_datetime) BETWEEN ? AND ?
        AND b.status = 'confirmed'
        ORDER BY b.booking_datetime ASC
    ''', (week_start, week_end))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_all_bookings(limit: int = 100, offset: int = 0):
    """Получить все записи (для администратора)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes,
            b.created_at
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        ORDER BY b.booking_datetime DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def search_bookings(search_term: str):
    """Поиск записей по имени клиента или услуге"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_pattern = f"%{search_term}%"
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE u.first_name LIKE ? 
           OR u.username LIKE ? 
           OR s.name LIKE ?
        ORDER BY b.booking_datetime DESC
        LIMIT 50
    ''', (search_pattern, search_pattern, search_pattern))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_bookings_by_date(date_str: str):
    """Получить записи на конкретную дату"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE DATE(b.booking_datetime) = ?
        ORDER BY b.booking_datetime ASC
    ''', (date_str,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_bookings_by_user_id(user_id: int):
    """Получить все записи пользователя (для администратора)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes,
            b.created_at
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE b.user_id = ?
        ORDER BY b.booking_datetime DESC
    ''', (user_id,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_bookings_by_status(status: str):
    """Получить записи по статусу"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE b.status = ?
        ORDER BY b.booking_datetime DESC
    ''', (status,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def count_bookings_by_status(status: str = None):
    """Посчитать количество записей по статусу"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute('SELECT COUNT(*) FROM bookings WHERE status = ?', (status,))
    else:
        cursor.execute('SELECT COUNT(*) FROM bookings')
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_recent_bookings(limit: int = 10):
    """Получить последние записи"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.booking_id,
            b.user_id,
            u.first_name,
            u.username,
            s.name as service_name,
            b.booking_datetime,
            b.status,
            s.price,
            s.duration_minutes,
            b.created_at
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        ORDER BY b.created_at DESC
        LIMIT ?
    ''', (limit,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_daily_statistics(date_str: str = None):
    """Получить статистику на день"""
    if not date_str:
        date_str = datetime.date.today().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Общее количество записей на день
    cursor.execute('''
        SELECT COUNT(*) 
        FROM bookings 
        WHERE DATE(booking_datetime) = ?
    ''', (date_str,))
    total_count = cursor.fetchone()[0]
    
    # Количество по статусам
    cursor.execute('''
        SELECT status, COUNT(*) 
        FROM bookings 
        WHERE DATE(booking_datetime) = ?
        GROUP BY status
    ''', (date_str,))
    status_counts = dict(cursor.fetchall())
    
    # Выручка на день
    cursor.execute('''
        SELECT SUM(s.price)
        FROM bookings b
        JOIN services s ON b.service_id = s.service_id
        WHERE DATE(b.booking_datetime) = ? AND b.status = 'confirmed'
    ''', (date_str,))
    daily_revenue = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'date': date_str,
        'total_count': total_count,
        'status_counts': status_counts,
        'daily_revenue': daily_revenue
    }

def get_booking_with_client_info(booking_id: int):
    """Получить запись с полной информацией о клиенте"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.*,
            u.first_name,
            u.last_name,
            u.username,
            u.phone,
            u.registration_date,
            s.name as service_name,
            s.price,
            s.duration_minutes,
            s.description as service_description
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN services s ON b.service_id = s.service_id
        WHERE b.booking_id = ?
    ''', (booking_id,))
    
    booking = cursor.fetchone()
    conn.close()
    return booking

def get_pending_bookings_count():
    """Получить количество записей, ожидающих подтверждения"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_today_bookings_count():
    """Получить количество записей на сегодня"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.date.today()
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE DATE(booking_datetime) = ? AND status = 'confirmed'", (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return count