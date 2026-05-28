# 🤖 АвтоДКP — Автоматизация договоров купли-продажи

> **Версия:** 2.0 Unified | **Платформы:** 📱 Telegram + 💻 Веб

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/agafonovdm142-crypto/Incom.git
cd Incom

# 2. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env — добавьте BOT_TOKEN

# 3. Запустите
sudo docker-compose up -d

# 4. Откройте в браузере
# Веб: http://localhost:8501
# Бот: отправьте /start в Telegram
```

### Вариант 2: Python (локально)

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Настройка
export BOT_TOKEN=your_token_here

# 3. Запуск веб-приложения (терминал 1)
streamlit run web/web_app.py

# 4. Запуск бота (терминал 2)
python bot/telegram_bot.py
```

### Вариант 3: Render.com (облако)

1. Форкните репозиторий на GitHub
2. Создайте аккаунт на [Render.com](https://render.com)
3. Нажмите "New Web Service" → "Build and deploy from a Git repository"
4. Укажите репозиторий и ветку `main`
5. Добавьте переменную окружения `BOT_TOKEN`
6. Нажмите "Create Web Service"

## 📁 Структура проекта

```
AutoDKP/
├── 📁 bot/
│   ├── __init__.py
│   └── telegram_bot.py          # Telegram-бот (aiogram)
│
├── 📁 web/
│   ├── __init__.py
│   └── web_app.py               # Streamlit веб-приложение
│
├── 📁 core/
│   ├── __init__.py
│   └── backend.py               # Ядро: модели, хранение, валидация
│
├── 📁 api/
│   ├── __init__.py
│   ├── ocr_agent.py             # Распознавание документов
│   ├── api_integrations.py      # ФНС, Росреестр, ГИС ГМП
│   └── esignature_module_v2.py # ЭП + подача в Росреестр
│
├── 📁 database/
│   └── schema.sql               # PostgreSQL схема
│
├── 📁 docs/
│   ├── README.md                # Этот файл
│   ├── USER_GUIDE.md            # Руководство пользователя
│   └── INSTALL.md               # Подробная установка
│
├── 📁 templates/                # Шаблоны договоров
│
├── .env.example                 # Шаблон настроек
├── docker-compose.yml           # Docker Compose
├── Dockerfile                 # Docker образ
├── render.yaml                # Конфиг Render.com
├── Procfile                   # Конфиг Heroku
├── requirements.txt           # Python зависимости
└── .github/workflows/deploy.yml # CI/CD GitHub Actions
```

## 📱💻 Синхронизация платформ

```
📱 Телефон: Создал сделку → ввёл данные → сохранил
     ↓ (JSON-файл deals.json)
💻 Компьютер: Открыл веб → данные на месте → продолжил
     ↓ (редактирование)
📱 Телефон: Проверил в боте → всё синхронизировано → готово!
```

## 🛠 Команды бота

- `/start` — Начать / Главное меню
- `/reset` — Сбросить состояние

## 🔧 Переменные окружения

| Переменная | Описание | Обязательно |
|-----------|----------|-------------|
| `BOT_TOKEN` | Токен Telegram-бота | ✅ Да |
| `DB_PASSWORD` | Пароль PostgreSQL | ❌ Нет |
| `FNS_API_KEY` | API-ключ ФНС | ❌ Нет |
| `ROSREESTR_API_KEY` | API-ключ Росреестра | ❌ Нет |
| `DEBUG` | Режим отладки | ❌ Нет |

## 📄 Лицензия

MIT — свободное использование.

---

**GitHub:** https://github.com/agafonovdm142-crypto/Incom  
**Telegram:** @AvtoDKP1_bot
