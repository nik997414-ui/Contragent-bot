import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("Warning: BOT_TOKEN is not set in .env file.")
