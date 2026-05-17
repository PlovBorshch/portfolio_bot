from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as req
from config import ADMIN_ID
from app.states import Reg, AddProject, Broadcast, EditProject

router = Router()


class Reg(StatesGroup):
    name = State()
    number = State()


class Broadcast(StatesGroup):
    message = State()


# Хендлер на кнопку "Мои скиллы"
@router.callback_query(F.data == 'skills')
async def skills(callback: types.CallbackQuery):
    await callback.answer("")
    await callback.message.edit_text(
        'Я умею:\n✅ Писать ботов на aiogram 3\n✅ Работать с Obsidian\n✅ Настраивать прокси',
        reply_markup=kb.in_line_back)


# Хендлер на кнопку "Обо мне
@router.callback_query(F.data == "info")
async def info(callback: types.CallbackQuery):
    await callback.answer('Вы выбрали обо мне')
    await callback.message.edit_text(
        'Я учусь программировать, чтобы не гнить дома. Быстро соображаю и делаю чисто \nМои проекты:',
        reply_markup=await kb.categories())


@router.callback_query(F.data.startswith("category_"))
async def show_projects_by_category(callback: types.CallbackQuery):
    await callback.answer("")
    await callback.message.edit_text("Выберите проект по категории",
                                     reply_markup=await kb.projects(callback.data.split("_")[1]))


@router.callback_query(F.data.startswith("project_"))
async def show_project_details(callback: types.CallbackQuery):
    project_data = await req.get_project(callback.data.split("_")[1])
    await callback.answer("")
    text = (f"<b>{project_data.name}</b>\n"
            f"📝 {project_data.description}\n"
            f"💰 Цена: {project_data.price}₽")

    await callback.message.edit_text(
        text,
        reply_markup=await kb.back_to_project_list_button(project_data.category),  # Кнопка назад к категориям
        parse_mode="HTML"  # Чтобы работал жирный шрифт
    )


@router.callback_query(F.data == "order")
async def order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Reg.name)  # Сразу включаем режим анкеты
    await callback.message.answer("Окей, давай оформим заявку. Как тебя зовут?")


# 2. Обработка имени (только текст!)
@router.message(Reg.name, F.text)
async def reg_two(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    # Даем кнопку для отправки номера
    await message.answer("Приятно познакомиться! Теперь нажми на кнопку ниже, чтобы отправить свой номер телефона.",
                         reply_markup=kb.get_number)


# 3. Финал (принимаем и текст, и контакт по кнопке)
@router.message(Reg.number, (F.text | F.contact))
async def two_three(message: types.Message, state: FSMContext):
    if message.contact:
        number = message.contact.phone_number
    else:
        number = message.text

    await state.update_data(number=number)
    data = await state.get_data()

    await message.answer(f'✅ Заявка принята!\nИмя: {data["name"]}\nНомер: {number}',
                         reply_markup=types.ReplyKeyboardRemove())  # Убираем кнопку номера

    MY_ID = 1222874197
    await message.bot.send_message(MY_ID, f"🔥 НОВАЯ ЗАЯВКА!\nИмя: {data['name']}\nТел: {number}")

    await state.clear()


@router.message(Command("start"))
async def start(message: types.Message):
    await req.set_user(message.from_user.id)
    await message.answer(
        f"Здарова, {message.from_user.first_name}! Я бот-визитка разработчика.",
        reply_markup=kb.inline_main
    )


@router.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(f"Здарова, {callback.from_user.first_name}! Я бот-визитка разработчика.",
                                     reply_markup=kb.inline_main
                                     )


@router.message(Command('admin'))
async def admin_panel_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await send_admin_panel(message)


# Для нажатия кнопки "Назад" в админке
@router.callback_query(F.data == "admin")
async def admin_panel_call(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.answer()
        await send_admin_panel(callback.message, edit=True)


# Выносим общую логику в отдельную функцию
async def send_admin_panel(message: types.Message, edit=False):
    total = await req.get_total_users()
    online = await req.get_online_users()
    text = (f"🛠 <b>Админ-панель</b>\n\n"
            f"👤 Всего пользователей: <code>{total}</code>\n"
            f"🟢 В сети: <code>{online}</code>\n"
            f"☠️Ты админ ты крутой")
    kb_markup = await kb.admin_main_keyboard()

    if edit:
        await message.edit_text(text, reply_markup=kb_markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=kb_markup, parse_mode="HTML")


@router.callback_query(F.data == "broadcast")
async def broadcast(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Broadcast.message)
    await callback.message.edit_text("Введите текст рассылки: ")


@router.message(Broadcast.message, F.text)
async def broadcast_final(message: types.Message, state: FSMContext):
    # 1. Сначала сохраняем в историю в БД
    await req.add_broadcast(text=message.text)

    # 2. Получаем список всех юзеров (через твою функцию в requests)
    users = await req.get_users()

    await message.answer(f"🚀 Запускаю рассылку на {len(users)} чел...")

    count = 0
    for user in users:
        try:
            # Копируем сообщение админа пользователю
            await message.copy_to(chat_id=user.tg_id)
            count += 1
        except Exception:
            pass  # Игнорим, если юзер забанил бота

    await message.answer(f"✅ Рассылка завершена. Доставлено: {count}", reply_markup=kb.in_line_admin)
    await state.clear()


# 1. Точка входа: Админ нажал "Добавить проект"
@router.callback_query(F.data == "admin_add_project")
async def add_project_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id == ADMIN_ID:
        await state.set_state(AddProject.category)
        await callback.message.edit_text("Выберите категорию для нового проекта:",
                                         reply_markup=await kb.admin_categories())
        await callback.answer()


# 2. Ловим выбранную категорию
@router.callback_query(AddProject.category, F.data.startswith("add_cat_"))
async def add_project_category(callback: types.CallbackQuery, state: FSMContext):
    category_id = callback.data.split("_")[2]  # Берем ID из 'add_cat_ID'
    await state.update_data(category=category_id)
    await state.set_state(AddProject.name)
    await callback.message.edit_text("Введите название проекта:")
    await callback.answer()


# 3. Ловим название
@router.message(AddProject.name)
async def add_project_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProject.description)
    await message.answer("Введите описание проекта:")


# 4. Ловим описание
@router.message(AddProject.description)
async def add_project_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProject.price)
    await message.answer("Введите цену проекта (только цифры):")


# 5. Финал: ловим цену и сохраняем
@router.message(AddProject.price)
async def add_project_final(message: types.Message, state: FSMContext):
    if message.text.isdigit():  # Проверка, что ввели число
        await state.update_data(price=message.text)
        data = await state.get_data()  # Вытаскиваем всё, что накопили

        await req.add_project(data)  # Отправляем в базу

        await message.answer(f"✅ Проект успешно добавлен!\n\n"
                             f"Категория ID: {data['category']}\n"
                             f"Название: {data['name']}\n"
                             f"Цена: {data['price']} руб.")
        await state.clear()  # Сбрасываем состояние
    else:
        await message.answer("Ошибка! Введите цену цифрами.")

'''
# 1. Админ нажал "Удалить проект" -> показываем категории
@router.callback_query(F.data == "admin_delete_project")
async def delete_project_start(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите категорию, в которой нужно УДАЛИТЬ проект:",
                                     reply_markup=await kb.admin_categories_gen("Delete")) # Нужна новая функция в kb.py
    await callback.answer()
'''

# 1. Выбор категории для удаления
@router.callback_query(F.data == "admin_delete_project")
async def delete_start(callback: types.CallbackQuery):
    await callback.message.edit_text("В какой категории удалить проект?",
                                     reply_markup=await kb.admin_categories_gen("delcat"))

# 2. Выбор проекта для удаления
@router.callback_query(F.data.startswith("delcat_"))
async def delete_step_2(callback: types.CallbackQuery):
    cat_id = callback.data.split("_")[1]
    await callback.message.edit_text("Выберите проект для УДАЛЕНИЯ:",
                                     reply_markup=await kb.admin_projects_gen(cat_id, "delitem"))

# 3. Финал удаления
@router.callback_query(F.data.startswith("delitem_"))
async def delete_step_3(callback: types.CallbackQuery):
    item_id = callback.data.split("_")[1]
    await req.delete_project(item_id)
    await callback.answer("❌ Проект удален")
    await send_admin_panel(callback.message, edit=True) # Возвращаем в админку


# 1. Начало правки (выбор категории)
@router.callback_query(F.data == "admin_edit_project")
async def edit_start(callback: types.CallbackQuery):
    await callback.message.edit_text("В какой категории проект для правки?",
                                     reply_markup=await kb.admin_categories_gen("editcat"))

# 2. Выбор проекта
@router.callback_query(F.data.startswith("editcat_"))
async def edit_step_2(callback: types.CallbackQuery):
    cat_id = callback.data.split("_")[1]
    await callback.message.edit_text("Какой проект редактируем?",
                                     reply_markup=await kb.admin_projects_gen(cat_id, "edititem"))

# 3. Выбор поля (допустим, пока только цена для простоты)
@router.callback_query(F.data.startswith("edititem_"))
async def edit_step_3(callback: types.CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[1])
    await state.update_data(project_id=item_id)  # Запомнили ID проекта

    await callback.message.edit_text("Что именно вы хотите изменить?",
                                     reply_markup=await kb.edit_project_keyboard())
    await callback.answer()


# 4. Ловим выбор ПОЛЯ
@router.callback_query(F.data.startswith("field_"))
async def edit_step_4(callback: types.CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[1]  # Получаем 'name', 'description' или 'price'
    await state.update_data(field=field)  # Запомнили, какое поле правим

    await state.set_state(EditProject.new_value)  # Переходим к ожиданию текста

    labels = {
        'name': 'новое название',
        'description': 'новое описание',
        'price': 'новую цену'
    }
    await callback.message.edit_text(f"Введите {labels[field]}:")
    await callback.answer()


# 5. Финал: сохранение любого поля
@router.message(EditProject.new_value)
async def edit_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    field = data['field']
    new_value = message.text

    # Валидация для цены (чтобы не ввели текст)
    if field == 'price':
        if not new_value.isdigit():
            return await message.answer("Ошибка! Цена должна быть числом.")
        new_value = int(new_value)

    # Вызываем универсальную функцию обновления из requests.py
    await req.update_project(data['project_id'], field, new_value)

    await message.answer(f"✅ Поле <b>{field}</b> успешно обновлено!", parse_mode="HTML")
    await state.clear()


from app.states import AddCategory


# 1. Вход в режим добавления категории
@router.callback_query(F.data == "admin_add_category")
async def add_category_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id == ADMIN_ID:
        await state.set_state(AddCategory.name)
        await callback.message.edit_text("Введите название новой категории:")
        await callback.answer()


# 2. Ловим название и сохраняем
@router.message(AddCategory.name)
async def add_category_final(message: types.Message, state: FSMContext):
    success = await req.add_category(message.text)

    if success:
        await message.answer(f"✅ Категория <b>{message.text}</b> успешно создана!",
                             parse_mode="HTML",
                             reply_markup=kb.in_line_admin)  # Кнопка возврата в админку
    else:
        await message.answer(f"⚠️ Категория с таким названием уже существует.")

    await state.clear()