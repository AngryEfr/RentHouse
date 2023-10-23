from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


storage = MemoryStorage()


class FSMFillForm(StatesGroup):
    show_bookings = State()
