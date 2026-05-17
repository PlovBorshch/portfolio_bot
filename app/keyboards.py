from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.database.requests import get_categories, get_category_project

# основные кнопки
inline_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚀 Мои скиллы", callback_data='skills'),
     InlineKeyboardButton(text="👤 Обо мне", callback_data='info')],
    [InlineKeyboardButton(text="💰 Заказать бота", callback_data='order')],
])

get_number = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📱 Отправить номер", request_contact=True)]
], resize_keyboard=True)

in_line_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back')]
])

my_project = {
    'Конвертор': 'https://github.com',
    'Телеграмм бот': 'https://github.com',
    'Парсер': 'https://github.com',

}


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.adjust(3)

    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return keyboard.as_markup()


async def projects(category_id):
    all_project = await get_category_project(category_id)
    keyboard = InlineKeyboardBuilder()
    for project in all_project:
        keyboard.add(InlineKeyboardButton(text=project.name, callback_data=f"project_{project.id}"))
    keyboard.adjust(3)

    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return keyboard.as_markup()


async def back_to_project_list_button(category_id):
    # Создаем кнопку
    button = InlineKeyboardButton(text="⬅️ К списку", callback_data=f"category_{category_id}")

    # Оборачиваем её в клавиатуру (список списков!)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    return keyboard


async def admin_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Добавить категорию", callback_data="admin_add_category")) # НОВАЯ
    builder.add(InlineKeyboardButton(text="➕ Добавить проект", callback_data="admin_add_project"))
    builder.add(InlineKeyboardButton(text="✏️ Изменить проект", callback_data="admin_edit_project"))
    builder.add(InlineKeyboardButton(text="❌ Удалить проект", callback_data="admin_delete_project"))
    builder.add(InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast"))
    builder.adjust(1)
    return builder.as_markup()

in_line_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Админ-панель', callback_data='admin')]
])

async def admin_categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        # Заметь: префикс 'add_cat_'
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"add_cat_{category.id}"))
    keyboard.adjust(2)
    return keyboard.as_markup()

# keyboards.py

# Универсальные категории с префиксом (чтобы знать, для чего выбираем: для удаления или правки)
async def admin_categories_gen(prefix):
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"{prefix}_{category.id}"))
    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin"))
    return keyboard.as_markup()

# Универсальные проекты с префиксом
async def admin_projects_gen(category_id, prefix):
    all_project = await get_category_project(category_id)
    keyboard = InlineKeyboardBuilder()
    for project in all_project:
        keyboard.add(InlineKeyboardButton(text=project.name, callback_data=f"{prefix}_{project.id}"))
    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin"))
    return keyboard.as_markup()


async def edit_project_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📝 Название", callback_data="field_name"))
    builder.add(InlineKeyboardButton(text="📖 Описание", callback_data="field_description"))
    builder.add(InlineKeyboardButton(text="💰 Цена", callback_data="field_price"))
    builder.adjust(1)
    return builder.as_markup()