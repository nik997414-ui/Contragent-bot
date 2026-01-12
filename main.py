import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
from tools import register_all_tools

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

async def main():
    if not BOT_TOKEN or "ur_token_here" in BOT_TOKEN:
        print("ОШИБКА: Токен не установлен! Пожалуйста, укажите ваш токен в файле .env")
        return

    # Объект бота
    bot = Bot(token=BOT_TOKEN)
    
    # Диспетчер
    dp = Dispatcher()

    # Хендлер на команду /start
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("Привет! Я модульный бот. Я умею использовать подключенные инструменты.")

    # Хендлер на команду /help
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer("Я загружаю инструменты из папки tools/. Просто добавь туда новый файл!")

    # Регистрируем все инструменты автоматически
    register_all_tools(dp)

    # Инициализация базы данных
    from database import init_db
    init_db()

    print("--- Бот запущен ---")

    # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
