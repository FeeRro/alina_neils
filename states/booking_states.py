from aiogram.fsm.state import State, StatesGroup

class BookingStates(StatesGroup):
    """Состояния для процесса записи"""
    selecting_service = State()
    selecting_date = State()
    selecting_time = State()
    confirming = State()