# 🤖 АвтоДКP — Автоматизация договоров купли-продажи

> **Версия:** 3.0 Unified | **Синхронизация:** Телефон ↔ Компьютер

## 🚀 Быстрый старт (2 минуты)

### 1. Нажми кнопку Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### 2. Токен уже настроен в .env
- Получи токен у [@BotFather](https://t.me/BotFather) в Telegram
- Добавь в переменные окружения Render: `BOT_TOKEN`

### 3. Готово!
Бот работает 24/7. Доступен с телефона и компьютера.

---

## 📱💻 Синхронизация

```
📱 Телефон: Создал сделку → ввёл данные → сохранил
💻 Компьютер: Открыл бота → данные на месте → продолжил
📱 Телефон: Проверил → всё синхронизировано → готово!
```

---

## 📁 Структура

```
├── bot/
│   └── telegram_bot.py      # Единый бот
├── core/
│   └── backend.py           # Синхронизация
├── render.yaml              # Конфиг Render
├── Procfile                 # Конфиг Heroku
├── requirements.txt         # Зависимости
└── .env.example             # Шаблон настроек
```

---

## 🛠 Локальный запуск

```bash
# Установка
pip install -r requirements.txt

# Настройка
cp .env.example .env
# Отредактируй .env — добавь BOT_TOKEN

# Запуск
python bot/telegram_bot.py
```

---

## 📄 Лицензия

MIT — свободное использование.
