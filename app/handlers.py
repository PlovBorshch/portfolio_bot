from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as req
from config import ADMIN_ID

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
            f"🟢 В сети: <code>{online}</code>"
            f"☠Ты админ ты крутой")
    kb_markup = await kb.admin_broadcast_inline_keyboard()

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
