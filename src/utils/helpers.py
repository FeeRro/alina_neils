import datetime

def format_booking_datetime(datetime_str: str) -> str:
    """Форматировать дату и время записи"""
    dt = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%d.%m.%Y %H:%M')

def calculate_end_time(start_datetime: str, duration_minutes: int) -> str:
    """Вычислить время окончания"""
    dt = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
    end_dt = dt + datetime.timedelta(minutes=duration_minutes)
    return end_dt.strftime('%H:%M')

def validate_date(date_str: str) -> bool:
    """Проверить корректность даты"""
    try:
        datetime.datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def validate_time(time_str: str) -> bool:
    """Проверить корректность времени"""
    try:
        datetime.datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False