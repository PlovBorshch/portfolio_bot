import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from config import TOKEN
from app.handlers import router
from app.database.models import async_main
from app.middlewares import TrackAllUsersMiddleware

async def main():
    bot = None  # Создаем пустую переменную заранее
    try:
        # 1. Сначала БД
        await async_main()

        # 2. Потом настройки связи
        PROXY_URL = "http://127.0.0.1:10808"
        session = AiohttpSession(proxy=PROXY_URL)

        # 3. Создаем бота и диспетчер
        bot = Bot(token=TOKEN,session=session)
        dp = Dispatcher()

        dp.update.outer_middleware(TrackAllUsersMiddleware())
        # 4. Подключаем роутеры (наши хендлеры)
        dp.include_router(router)


        await dp.start_polling(bot)
        print("Бот успешно запущен!")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
    finally:
        if bot:  # Закрываем сессию только если бот успел создаться
            await bot.session.close()

if __name__ == "__main__":
    try:

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")