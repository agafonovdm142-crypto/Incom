# 🔧 Подробная установка АвтоДКP

## Системные требования

- Python 3.11+
- Docker (опционально)
- 2 GB RAM минимум
- 5 GB свободного места

## Установка шаг за шагом

### 1. Клонирование репозитория

```bash
git clone https://github.com/agafonovdm142-crypto/Incom.git
cd Incom
```

### 2. Настройка окружения

```bash
cp .env.example .env
nano .env  # или используйте редактор
```

Заполните:
```env
BOT_TOKEN=8764706036:AAHJ0jrn1A0PwCBzldIvoyTx20FpCZd8ELg
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Установка Tesseract OCR (для OCR)

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-rus
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Скачайте установщик с https://github.com/UB-Mannheim/tesseract/wiki

### 5. Запуск

**Веб-приложение:**
```bash
streamlit run web/web_app.py
```

**Telegram-бот:**
```bash
python bot/telegram_bot.py
```

### 6. Docker (альтернатива)

```bash
docker-compose up -d
```

## Деплой на Render.com

1. Пушьте код на GitHub
2. Создайте аккаунт на Render.com
3. New Web Service → Build from Git repo
4. Выберите репозиторий
5. Установите Environment Variables:
   - `BOT_TOKEN`
6. Create Web Service

## Деплой на Heroku

```bash
heroku create autodkp
heroku config:set BOT_TOKEN=your_token
heroku stack:set container
git push heroku main
```
