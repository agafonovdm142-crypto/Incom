"""
🤖 АвтоДКP Simple — Бот на requests (работает ВЕЗДЕ)
Без aiohttp, без asyncio, без сложных зависимостей
"""

import os
import time
import json
from datetime import datetime
import requests

API_TOKEN = os.getenv("BOT_TOKEN", "8764706036:AAHJ0jrn1A0PwCBzldIvoyTx20FpCZd8ELg")
API_URL = f"https://api.telegram.org/bot{API_TOKEN}"

# Хранилище
users = {}
deals = {}

def get_updates(offset=None):
    """Получение сообщений от Telegram"""
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except:
        return []

def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения"""
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(f"{API_URL}/sendMessage", data=data, timeout=10)
    except:
        pass

def handle_message(msg):
    """Обработка сообщения"""
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    user_id = msg["from"]["id"]

    # Получаем или создаём пользователя
    if user_id not in users:
        users[user_id] = {"step": "menu", "deal": None}

    user = users[user_id]

    # Команда /start
    if text == "/start":
        user["step"] = "menu"
        send_message(chat_id, 
            "👋 Привет! Я АвтоДКP<br>"
            "📱 Создам договор купли-продажи<br><br>"
            "Выберите действие:",
            {"keyboard": [["➕ Новый ДКП"], ["📋 Мои сделки"]], "resize_keyboard": True}
        )
        return

    # Главное меню
    if user["step"] == "menu":
        if text == "➕ Новый ДКП":
            deal_id = f"DKP-{user_id}-{int(time.time())}"
            deals[deal_id] = {"user": user_id, "date": datetime.now().isoformat()}
            user["deal"] = deal_id
            user["step"] = "seller"
            send_message(chat_id, "👤 Введите ФИО продавца:")

        elif text == "📋 Мои сделки":
            user_deals = [k for k, v in deals.items() if v.get("user") == user_id]
            if user_deals:
                msg = "📋 Ваши сделки:<br>"
                for d in user_deals[-5:]:
                    deal = deals[d]
                    msg += f"<br>🟡 {d}<br>"
                    msg += f"   Продавец: {deal.get('seller', '—')}<br>"
                    msg += f"   Цена: {deal.get('price', 0):,} ₽<br>"
                send_message(chat_id, msg)
            else:
                send_message(chat_id, "У вас пока нет сделок")

        else:
            send_message(chat_id, "Нажмите кнопку ➕ Новый ДКП")

    # Шаги заполнения
    elif user["step"] == "seller":
        deals[user["deal"]]["seller"] = text
        user["step"] = "buyer"
        send_message(chat_id, "👤 Введите ФИО покупателя:")

    elif user["step"] == "buyer":
        deals[user["deal"]]["buyer"] = text
        user["step"] = "address"
        send_message(chat_id, "🏠 Введите адрес квартиры:")

    elif user["step"] == "address":
        deals[user["deal"]]["address"] = text
        user["step"] = "price"
        send_message(chat_id, "💰 Введите цену (только цифры):")

    elif user["step"] == "price":
        try:
            price = int(text.replace(" ", "").replace("₽", ""))
            deals[user["deal"]]["price"] = price
            user["step"] = "bank"
            send_message(chat_id, "🏦 Выберите банк:",
                {"keyboard": [["🏦 Сбербанк", "🏦 ВТБ", "🏦 Альфа-Банк"]], "resize_keyboard": True}
            )
        except:
            send_message(chat_id, "❌ Только цифры! Пример: 12500000")

    elif user["step"] == "bank":
        banks = {"🏦 Сбербанк": "Сбербанк", "🏦 ВТБ": "ВТБ", "🏦 Альфа-Банк": "Альфа-Банк"}
        if text in banks:
            deal = deals[user["deal"]]
            deal["bank"] = banks[text]

            # Генерируем договор
            contract = f"""ДОГОВОР КУПЛИ-ПРОДАЖИ

Продавец: {deal.get("seller", "")}
Покупатель: {deal.get("buyer", "")}
Адрес: {deal.get("address", "")}
Цена: {deal.get("price", 0):,} руб.
Банк: {deal.get("bank", "")}

Дата: {datetime.now().strftime("%d.%m.%Y")}
"""
            deal["contract"] = contract

            send_message(chat_id, 
                f"✅ Договор готов!<br><br>{contract}<br><br>"
                f"Сохраните этот текст и распечатайте.",
                {"keyboard": [["➕ Новый ДКП"], ["📋 Мои сделки"]], "resize_keyboard": True}
            )
            user["step"] = "menu"
        else:
            send_message(chat_id, "Выберите банк кнопкой")

    else:
        send_message(chat_id, "Отправьте /start")

def main():
    print("🤖 АвтоДКP Simple запущен!")
    print("   Работает на requests (без aiohttp)")

    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            if "message" in update:
                handle_message(update["message"])
        time.sleep(1)

if __name__ == "__main__":
    main()
