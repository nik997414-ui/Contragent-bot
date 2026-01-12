#!/bin/bash
# Скрипт деплоя бота на VPS
# Запускать на сервере: bash deploy.sh

cd /opt/bot

# Остановить бота если запущен
pkill -f "python main.py" 2>/dev/null

# Получить последние изменения
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/nik997414-ui/Contragent-bot.git .
fi

# Активировать виртуальное окружение
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt -q

# Запустить бота в фоне
nohup python main.py > bot.log 2>&1 &

echo "✅ Бот обновлён и запущен!"
echo "Логи: tail -f /opt/bot/bot.log"
