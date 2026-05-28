#!/bin/bash
# 🔧 Скрипт для загрузки проекта на GitHub

REPO_URL="https://github.com/agafonovdm142-crypto/Incom.git"
TOKEN="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"

echo "🚀 Загрузка АвтоДКP на GitHub..."

# Инициализация (если нужно)
if [ ! -d .git ]; then
    git init
    git remote add origin https://agafonovdm142-crypto:${TOKEN}@github.com/agafonovdm142-crypto/Incom.git
fi

# Добавление файлов
git add -A

# Коммит
git commit -m "🤖 АвтоДКP v2.0 — Unified платформа (Telegram + Web)

- Исправлен Telegram-бот (кнопки, FSM, fallback)
- Улучшено веб-приложение (Streamlit, 6-шаговый мастер)
- Добавлено ядро (модели, валидация, генерация)
- Интеграции: OCR, API, электронная подпись
- Docker + Render.com + Heroku ready
- Полная документация"

# Пуш
git branch -M main
git push -u origin main --force

echo "✅ Готово! Проверьте: ${REPO_URL}"
