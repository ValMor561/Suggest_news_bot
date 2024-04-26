from aiogram.filters.state import State, StatesGroup

class CreateNews(StatesGroup):
    text = State()
    images = State()
    result = State()
