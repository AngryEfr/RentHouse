from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


storage = MemoryStorage()


class FSMFillForm(StatesGroup):
    fill_name = State()
    fill_id_house = State()
    fill_date = State()
    confirm = State()
