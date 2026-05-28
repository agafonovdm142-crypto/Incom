"""
🤖 АвтоДКP Lite — Минимальный бот для Render
Только текстовый ввод, максимальная совместимость
"""

import os
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

API_TOKEN = os.getenv("BOT_TOKEN", "8764706036:AAHJ0jrn1A0PwCBzldIvoyTx20FpCZd8ELg")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Хранилище сделок
deals = {}

class States(StatesGroup):
    menu = State()
    seller = State()
    buyer = State()
    property = State()
    price = State()
    bank = State()
    confirm = State()

# Клавиатуры
def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Новый ДКП", "📋 Мои сделки")
    return kb

def bank_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🏦 Сбербанк", "🏦 ВТБ")
    kb.add("🏦 Альфа-Банк")
    return kb

# Обработчики
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await States.menu.set()
    await message.answer(
        "👋 Привет! Я АвтоДКP\n"
        "Создам договор купли-продажи\n\n"
        "Нажмите ➕ Новый ДКП",
        reply_markup=main_kb()
    )

@dp.message_handler(state=States.menu)
async def menu(message: types.Message, state: FSMContext):
    text = message.text
    if text == "➕ Новый ДКП":
        deal_id = f"DKP-{message.from_user.id}-{int(datetime.now().timestamp())}"
        await state.update_data(deal_id=deal_id)
        deals[deal_id] = {"user": message.from_user.id, "date": datetime.now().isoformat()}
        await States.seller.set()
        await message.answer("👤 Введите ФИО продавца:")
    elif text == "📋 Мои сделки":
        user_deals = [k for k, v in deals.items() if v.get("user") == message.from_user.id]
        if user_deals:
            await message.answer(f"📋 Сделки: {len(user_deals)}")
        else:
            await message.answer("Нет сделок")
    else:
        await message.answer("Нажмите кнопку")

@dp.message_handler(state=States.seller)
async def seller(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deals[data["deal_id"]]["seller"] = message.text
    await States.buyer.set()
    await message.answer("👤 Введите ФИО покупателя:")

@dp.message_handler(state=States.buyer)
async def buyer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deals[data["deal_id"]]["buyer"] = message.text
    await States.property.set()
    await message.answer("🏠 Введите адрес:")

@dp.message_handler(state=States.property)
async def property_addr(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deals[data["deal_id"]]["address"] = message.text
    await States.price.set()
    await message.answer("💰 Введите цену (только цифры):")

@dp.message_handler(state=States.price)
async def price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text.replace(" ", ""))
        data = await state.get_data()
        deals[data["deal_id"]]["price"] = price
        await States.bank.set()
        await message.answer("🏦 Выберите банк:", reply_markup=bank_kb())
    except:
        await message.answer("❌ Только цифры!")

@dp.message_handler(state=States.bank)
async def bank(message: types.Message, state: FSMContext):
    banks = {"🏦 Сбербанк": "Сбербанк", "🏦 ВТБ": "ВТБ", "🏦 Альфа-Банк": "Альфа-Банк"}
    if message.text in banks:
        data = await state.get_data()
        deal = deals[data["deal_id"]]
        deal["bank"] = banks[message.text]

        contract = f"""ДОГОВОР КУПЛИ-ПРОДАЖИ

Продавец: {deal.get("seller", "")}
Покупатель: {deal.get("buyer", "")}
Адрес: {deal.get("address", "")}
Цена: {deal.get("price", 0):,} руб.
Банк: {deal.get("bank", "")}

Дата: {datetime.now().strftime("%d.%m.%Y")}
"""
        deal["contract"] = contract

        await message.answer(f"✅ Договор готов!\n\n{contract}")
        await States.menu.set()
        await message.answer("Главное меню:", reply_markup=main_kb())
    else:
        await message.answer("Выберите банк кнопкой")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Отправьте /start")

if __name__ == '__main__':
    print("🤖 Бот запущен!")
    executor.start_polling(dp, skip_updates=True)
