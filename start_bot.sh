#!/bin/bash
# 🤖 Локальный запуск AutoDKP бота
# Запустите на своём компьютере/телефоне

echo "🚀 Запуск AutoDKP Bot..."

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите:"
    echo "   Ubuntu: sudo apt install python3 python3-pip"
    echo "   macOS: brew install python3"
    echo "   Windows: скачайте с python.org"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip3 install aiogram==2.25.1 python-dotenv

# Создаём .env если нет
if [ ! -f .env ]; then
    echo "BOT_TOKEN=8764706036:AAHJ0jrn1A0PwCBzldIvoyTx20FpCZd8ELg" > .env
    echo "✅ Создан .env с токеном"
fi

# Запускаем
echo "🤖 Бот запущен! Нажмите Ctrl+C для остановки"
cd bot
python3 telegram_bot.py
