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


async def admin_broadcast_inline_keyboard():

    button = InlineKeyboardButton(text="Рассылка", callback_data="broadcast")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    return keyboard

in_line_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Админ-панель', callback_data='admin')]
])
