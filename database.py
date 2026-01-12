import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")

# Список username администраторов с безлимитным доступом (без @)
ADMIN_USERNAMES = ["zegnas"]

def init_db():
    """Инициализирует базу данных и таблицу пользователей, если их нет."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                checks_left INTEGER DEFAULT 3,
                is_premium BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()


def is_admin(username: str) -> bool:
    """Проверяет, является ли пользователь администратором."""
    if not username:
        return False
    return username.lower() in [u.lower() for u in ADMIN_USERNAMES]


def get_or_create_user(user_id: int):
    """Возвращает информацию о пользователе или создает нового."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT checks_left, is_premium FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        if result:
            return {"checks_left": result[0], "is_premium": bool(result[1])}
        else:
            # Новый пользователь - 3 проверки
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            return {"checks_left": 3, "is_premium": False}

def try_consume_check(user_id: int) -> bool:
    """
    Пытается списать 1 проверку.
    Возвращает True, если проверка разрешена (есть лимиты или премиум).
    Возвращает False, если лимиты исчерпаны.
    """
    user = get_or_create_user(user_id)
    
    if user["is_premium"]:
        return True
        
    if user["checks_left"] > 0:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET checks_left = checks_left - 1 WHERE user_id = ?", (user_id,))
            conn.commit()
        return True
    
    return False
