from aiogram.fsm.state import StatesGroup, State

# Стейты для регистрации обычного юзера
class Reg(StatesGroup):
    name = State()
    number = State()

# Стейты для админа: добавление нового проекта
class AddProject(StatesGroup):
    category = State()    # Выбор категории
    name = State()        # Ввод названия
    description = State() # Ввод описания
    price = State()       # Ввод цены

class Broadcast(StatesGroup):
    message = State()

# states.py

class EditProject(StatesGroup):
    project_id = State()
    field = State()
    new_value = State()

class AddCategory(StatesGroup):
    name = State()