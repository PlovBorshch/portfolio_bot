from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime

# 1. Движок. sqlite+aiosqlite — используем асинхронный драйвер.
# Три слэша /// — это путь к файлу в текущей папке.
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

# 2. Фабрика сессий. Через неё мы будем "общаться" с базой.
async_session = async_sessionmaker(engine)


# 3. Базовый класс. Собирает в себя все модели.
class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'  # Имя таблицы в БД

    # id: тип для Python = настройка для SQL
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    date_reg: Mapped[datetime] = mapped_column(default=datetime.now)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))  # Ограничение 25 символов


class Project(Base):
    __tablename__ = 'Projects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(String(120))
    price: Mapped[int] = mapped_column()
    # ForeignKey — связь. Говорим: "в этой колонке ID из таблицы categories"
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))

class Broadcast(Base):
    __tablename__ = 'Broadcasts'
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    date_broadcast: Mapped[datetime] = mapped_column(default=datetime.now)


# Функция создания таблиц
async def async_main():
    async with engine.begin() as conn:
        # metadata.create_all — создает все таблицы, которые наследуют Base
        await conn.run_sync(Base.metadata.create_all)