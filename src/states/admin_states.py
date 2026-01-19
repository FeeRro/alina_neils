from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    """Состояния для админ-панели"""
    waiting_password = State()
    admin_menu = State()
    sending_notification = State()
    rescheduling_booking = State()
    selecting_reschedule_date = State()
    selecting_reschedule_time = State()