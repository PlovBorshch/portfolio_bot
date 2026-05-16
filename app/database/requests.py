from app.database.models import async_session
from app.database.models import User, Category, Project, Broadcast
from sqlalchemy import select, update, delete
from datetime import datetime, timedelta
from sqlalchemy import func  # Для подсчета


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            # Если юзера нет — создаем
            session.add(User(tg_id=tg_id))
            await session.commit()
        else:
            # Если юзер есть — ОБНОВЛЯЕМ время активности
            user.last_seen = datetime.now()
            await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_project(category_id):
    async with async_session() as session:
        return await session.scalars(select(Project).where(Project.category == category_id))


async def get_project(project_id):
    async with async_session() as session:
        return await session.scalar(select(Project).where(Project.id == project_id))


# Считаем всех
async def get_total_users():
    async with async_session() as session:
        # Инсайд: select(func.count()) работает быстрее, чем выкачивать всех юзеров
        result = await session.execute(select(func.count(User.id)))
        return result.scalar()

async def get_users():
    async with async_session() as session:
        # Получаем всех пользователей
        result = await session.scalars(select(User))
        return result.all()


# Считаем активных (онлайн)
async def get_online_users():
    async with async_session() as session:
        # Считаем тех, кто писал боту в последние 5 минут
        threshold = datetime.now() - timedelta(minutes=10)
        result = await session.execute(
            select(func.count(User.id)).where(User.last_seen >= threshold)
        )
        return result.scalar()

async def add_broadcast(text):
    async with async_session() as session:
        session.add(Broadcast(text=text))
        await session.commit()