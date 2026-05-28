"""
🤖 АвтоДКП Бот — Telegram-интерфейс для автоматизации ДКП
Версия: 2.0 | aiogram 2.25.1 | Исправленная версия
"""

import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# ── Конфигурация ──
API_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ── Состояния FSM ──
class DealStates(StatesGroup):
    menu = State()
    seller_passport = State()
    seller_confirm = State()
    buyer_passport = State()
    buyer_confirm = State()
    property_info = State()
    price = State()
    escrow = State()
    validation = State()
    generate = State()

# ── Клавиатуры ──
def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("➕ Новый ДКП", "📋 Мои сделки")
    kb.add("⚙️ Настройки", "❓ Помощь")
    return kb

def confirm_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("✅ Верно", "✏️ Исправить")
    kb.add("◀️ Назад в меню")
    return kb

def escrow_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("🏦 Сбербанк", "🏦 ВТБ")
    kb.add("🏦 Альфа-Банк", "✏️ Другой")
    kb.add("◀️ Назад")
    return kb

def back_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✏️ Ввести вручную", "◀️ Назад")
    return kb

def validation_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("📄 Сгенерировать ДКП")
    kb.add("✏️ Исправить данные", "◀️ Назад")
    return kb

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def format_price(price):
    """Форматирование цены с пробелами"""
    return f"{price:,}".replace(",", " ")

def parse_manual_input(text):
    """Парсинг ручного ввода: ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес"""
    parts = text.split(";")
    if len(parts) >= 7:
        return {
            "full_name": parts[0].strip(),
            "birth_date": parts[1].strip(),
            "passport_series": parts[2].strip(),
            "passport_number": parts[3].strip(),
            "passport_issued_by": parts[4].strip(),
            "passport_issued_date": parts[5].strip(),
            "registration_address": parts[6].strip()
        }
    return None

# ═══════════════════════════════════════════════════════════════
# ОБРАБОТЧИКИ КОМАНД
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    """Старт — сброс и главное меню"""
    await state.finish()
    await state.reset_state(with_data=True)
    await DealStates.menu.set()

    await message.answer(
        "👋 Привет! Я АвтоДКП\n"
        "🤖 Автоматизация договоров купли-продажи\n\n"
        "📱 Загружай фото документов — получай готовый ДКП\n"
        "Выберите действие:",
        reply_markup=main_kb()
    )

@dp.message_handler(commands=['reset'])
async def cmd_reset(message: types.Message, state: FSMContext):
    """Сброс состояния"""
    await state.finish()
    await message.answer(
        "✅ Состояние сброшено. Отправьте /start",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ═══════════════════════════════════════════════════════════════
# ГЛАВНОЕ МЕНЮ
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(Text(equals="➕ Новый ДКП"), state=DealStates.menu)
async def menu_new_deal(message: types.Message, state: FSMContext):
    """Начало новой сделки"""
    await DealStates.seller_passport.set()
    await message.answer(
        "📋 Новая сделка — Шаг 1/6\n\n"
        "👤 Продавец\n"
        "Пришлите фото паспорта (разворот с фото)\n"
        "Или нажмите ✏️ для ручного ввода",
        reply_markup=back_kb()
    )

@dp.message_handler(Text(equals="📋 Мои сделки"), state=DealStates.menu)
async def menu_my_deals(message: types.Message, state: FSMContext):
    """Показать сделки"""
    await message.answer(
        "📋 Ваши сделки:\n\n"
        "🟡 DKP-2026-0042 — г. Москва, ул. Окская, д. 36\n"
        "   💰 12 500 000 ₽ | Статус: Черновик\n\n"
        "🟢 DKP-2026-0041 — г. Москва, ул. Ленина, д. 15\n"
        "   💰 8 900 000 ₽ | Статус: Подписан",
        reply_markup=main_kb()
    )

@dp.message_handler(Text(equals="⚙️ Настройки"), state=DealStates.menu)
async def menu_settings(message: types.Message, state: FSMContext):
    """Настройки"""
    await message.answer(
        "⚙️ Настройки:\n\n"
        "👤 Профиль: Олеся\n"
        "📞 Телефон: +7 (999) 123-45-67\n"
        "📧 Email: olesya@example.com\n\n"
        "🏦 Банк по умолчанию: Сбербанк\n"
        "🏦 Эскроу: Домклик\n\n"
        "🔔 Уведомления: Push ✓ | Email ✓ | SMS ✗",
        reply_markup=main_kb()
    )

@dp.message_handler(Text(equals="❓ Помощь"), state=DealStates.menu)
async def menu_help(message: types.Message, state: FSMContext):
    """Помощь"""
    await message.answer(
        "❓ Как пользоваться:\n\n"
        "1️⃣ Нажмите ➕ Новый ДКП\n"
        "2️⃣ Загрузите фото паспорта продавца\n"
        "3️⃣ Проверьте распознанные данные\n"
        "4️⃣ Загрузите фото паспорта покупателя\n"
        "5️⃣ Укажите адрес квартиры или загрузите ЕГРН\n"
        "6️⃣ Укажите цену (аванс рассчитается автоматически)\n"
        "7️⃣ Выберите банк для эскроу\n"
        "8️⃣ Система проверит данные и сгенерирует договор\n\n"
        "📄 Готовый PDF можно сразу отправить сторонам",
        reply_markup=main_kb()
    )

@dp.message_handler(state=DealStates.menu)
async def menu_unknown(message: types.Message, state: FSMContext):
    """Неизвестная команда в меню"""
    await message.answer(
        f"❓ Я не понял: '{message.text}'\n"
        "Нажмите одну из кнопок ниже",
        reply_markup=main_kb()
    )

# ═══════════════════════════════════════════════════════════════
# ШАГ 1: ПАСПОРТ ПРОДАВЦА
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(content_types=['photo'], state=DealStates.seller_passport)
async def seller_photo(message: types.Message, state: FSMContext):
    """Обработка фото паспорта продавца"""
    await message.answer("🖼 Фото получено. Распознаю...")

    # Здесь будет вызов OCR-агента
    # Пока имитируем распознавание
    seller_data = {
        "full_name": "Петров Петр Петрович",
        "birth_date": "15.03.1985",
        "passport_series": "45 06",
        "passport_number": "123456",
        "passport_issued_by": "ОТДЕЛЕНИЕ УФМС РОССИИ ПО ГОР. МОСКВЕ",
        "passport_issued_date": "10.02.2010",
        "registration_address": "г. Москва, ул. Сокольнический вал, д. 10, кв. 45"
    }

    await state.update_data(seller=seller_data)
    await DealStates.seller_confirm.set()

    await message.answer(
        "✅ Распознано!\n\n"
        f"👤 {seller_data['full_name']}\n"
        f"📅 {seller_data['birth_date']}\n"
        f"🛂 Паспорт: {seller_data['passport_series']} {seller_data['passport_number']}\n"
        f"🏛 Выдан: {seller_data['passport_issued_date']}\n"
        f"📍 Адрес: {seller_data['registration_address']}\n\n"
        "Данные верны?",
        reply_markup=confirm_kb()
    )

@dp.message_handler(Text(equals="✏️ Ввести вручную"), state=DealStates.seller_passport)
async def seller_manual_start(message: types.Message, state: FSMContext):
    """Начало ручного ввода продавца"""
    await message.answer(
        "Введите данные продавца в формате:\n"
        "ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес\n\n"
        "Пример:\n"
        "Иванов Иван Иванович;01.01.1990;45 06;123456;ОВД ЦАО;10.02.2010;г. Москва, ул. Ленина 1",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(Text(equals="◀️ Назад"), state=DealStates.seller_passport)
async def seller_back(message: types.Message, state: FSMContext):
    """Назад в меню"""
    await DealStates.menu.set()
    await message.answer("Главное меню:", reply_markup=main_kb())

@dp.message_handler(content_types=['text'], state=DealStates.seller_passport)
async def seller_manual_input(message: types.Message, state: FSMContext):
    """Обработка ручного ввода продавца"""
    parsed = parse_manual_input(message.text)

    if parsed:
        await state.update_data(seller=parsed)
        await DealStates.seller_confirm.set()
        await message.answer(
            "✅ Данные сохранены!\n\n"
            f"👤 {parsed['full_name']}\n"
            f"📅 {parsed['birth_date']}\n"
            f"🛂 Паспорт: {parsed['passport_series']} {parsed['passport_number']}\n\n"
            "Данные верны?",
            reply_markup=confirm_kb()
        )
    else:
        await message.answer(
            "❌ Неверный формат. Введите данные через точку с запятой:\n"
            "ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес",
            reply_markup=types.ReplyKeyboardRemove()
        )

# ═══════════════════════════════════════════════════════════════
# ПОДТВЕРЖДЕНИЕ ПРОДАВЦА
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(Text(equals="✅ Верно"), state=DealStates.seller_confirm)
async def seller_confirm_yes(message: types.Message, state: FSMContext):
    """Подтверждение данных продавца"""
    await DealStates.buyer_passport.set()
    await message.answer(
        "👤 Шаг 2/6: Покупатель\n\n"
        "Пришлите фото паспорта покупателя\n"
        "Или нажмите ✏️ для ручного ввода",
        reply_markup=back_kb()
    )

@dp.message_handler(Text(equals="✏️ Исправить"), state=DealStates.seller_confirm)
async def seller_confirm_edit(message: types.Message, state: FSMContext):
    """Исправление данных продавца"""
    await message.answer(
        "Введите исправленные данные:\n"
        "ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(Text(equals="◀️ Назад в меню"), state=DealStates.seller_confirm)
async def seller_confirm_back(message: types.Message, state: FSMContext):
    """Назад в меню"""
    await DealStates.menu.set()
    await message.answer("Главное меню:", reply_markup=main_kb())

@dp.message_handler(content_types=['text'], state=DealStates.seller_confirm)
async def seller_confirm_input(message: types.Message, state: FSMContext):
    """Обработка исправленных данных продавца"""
    parsed = parse_manual_input(message.text)
    if parsed:
        await state.update_data(seller=parsed)
        await DealStates.buyer_passport.set()
        await message.answer(
            "✅ Данные обновлены!\n\n"
            "👤 Шаг 2/6: Покупатель\n"
            "Пришлите фото паспорта покупателя",
            reply_markup=back_kb()
        )
    else:
        await message.answer(
            "❌ Неверный формат. Попробуйте ещё раз:\n"
            "ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес"
        )

# ═══════════════════════════════════════════════════════════════
# ШАГ 2: ПАСПОРТ ПОКУПАТЕЛЯ
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(content_types=['photo'], state=DealStates.buyer_passport)
async def buyer_photo(message: types.Message, state: FSMContext):
    """Обработка фото паспорта покупателя"""
    await message.answer("🖼 Фото получено. Распознаю...")

    buyer_data = {
        "full_name": "Иванов Иван Иванович",
        "birth_date": "22.07.1990",
        "passport_series": "40 02",
        "passport_number": "654321",
        "passport_issued_by": "ОТДЕЛЕНИЕ УФМС РОССИИ ПО ГОР. МОСКВЕ",
        "passport_issued_date": "15.03.2015",
        "registration_address": "г. Москва, ул. Ленинградская, д. 15, кв. 78"
    }

    await state.update_data(buyer=buyer_data)
    await DealStates.buyer_confirm.set()

    await message.answer(
        "✅ Распознано!\n\n"
        f"👤 {buyer_data['full_name']}\n"
        f"📅 {buyer_data['birth_date']}\n"
        f"🛂 Паспорт: {buyer_data['passport_series']} {buyer_data['passport_number']}\n\n"
        "Данные верны?",
        reply_markup=confirm_kb()
    )

@dp.message_handler(Text(equals="✏️ Ввести вручную"), state=DealStates.buyer_passport)
async def buyer_manual_start(message: types.Message, state: FSMContext):
    """Начало ручного ввода покупателя"""
    await message.answer(
        "Введите данные покупателя в формате:\n"
        "ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(Text(equals="◀️ Назад"), state=DealStates.buyer_passport)
async def buyer_back(message: types.Message, state: FSMContext):
    """Назад к продавцу"""
    await DealStates.seller_passport.set()
    await message.answer(
        "👤 Шаг 1/6: Продавец\n"
        "Пришлите фото паспорта продавца",
        reply_markup=back_kb()
    )

@dp.message_handler(content_types=['text'], state=DealStates.buyer_passport)
async def buyer_manual_input(message: types.Message, state: FSMContext):
    """Обработка ручного ввода покупателя"""
    parsed = parse_manual_input(message.text)

    if parsed:
        await state.update_data(buyer=parsed)
        await DealStates.buyer_confirm.set()
        await message.answer(
            "✅ Данные сохранены!\n\n"
            f"👤 {parsed['full_name']}\n"
            f"📅 {parsed['birth_date']}\n"
            f"🛂 Паспорт: {parsed['passport_series']} {parsed['passport_number']}\n\n"
            "Данные верны?",
            reply_markup=confirm_kb()
        )
    else:
        await message.answer(
            "❌ Неверный формат. Введите данные через точку с запятой:\n"
            "ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес"
        )

# ═══════════════════════════════════════════════════════════════
# ПОДТВЕРЖДЕНИЕ ПОКУПАТЕЛЯ
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(Text(equals="✅ Верно"), state=DealStates.buyer_confirm)
async def buyer_confirm_yes(message: types.Message, state: FSMContext):
    """Подтверждение данных покупателя"""
    await DealStates.property_info.set()
    await message.answer(
        "🏠 Шаг 3/6: Объект недвижимости\n\n"
        "Введите адрес квартиры\n"
        "Или загрузите выписку ЕГРН",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("📷 Загрузить ЕГРН", "◀️ Назад")
    )

@dp.message_handler(Text(equals="✏️ Исправить"), state=DealStates.buyer_confirm)
async def buyer_confirm_edit(message: types.Message, state: FSMContext):
    """Исправление данных покупателя"""
    await message.answer(
        "Введите исправленные данные:\n"
        "ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(Text(equals="◀️ Назад в меню"), state=DealStates.buyer_confirm)
async def buyer_confirm_back(message: types.Message, state: FSMContext):
    """Назад в меню"""
    await DealStates.menu.set()
    await message.answer("Главное меню:", reply_markup=main_kb())

@dp.message_handler(content_types=['text'], state=DealStates.buyer_confirm)
async def buyer_confirm_input(message: types.Message, state: FSMContext):
    """Обработка исправленных данных покупателя"""
    parsed = parse_manual_input(message.text)
    if parsed:
        await state.update_data(buyer=parsed)
        await DealStates.property_info.set()
        await message.answer(
            "✅ Данные обновлены!\n\n"
            "🏠 Шаг 3/6: Объект недвижимости\n"
            "Введите адрес квартиры",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("📷 Загрузить ЕГРН", "◀️ Назад")
        )
    else:
        await message.answer(
            "❌ Неверный формат. Попробуйте ещё раз:\n"
            "ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес"
        )

# ═══════════════════════════════════════════════════════════════
# ШАГ 3: ОБЪЕКТ НЕДВИЖИМОСТИ
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(content_types=['photo'], state=DealStates.property_info)
async def property_photo(message: types.Message, state: FSMContext):
    """Обработка фото ЕГРН"""
    await message.answer("🖼 Фото получено. Распознаю выписку...")

    property_data = {
        "address": "г. Москва, ул. Окская, д. 36, корп. 4, кв. 45",
        "cadastral": "77:04:0002017:4567",
        "area": 52.5
    }

    await state.update_data(property=property_data)
    await DealStates.price.set()

    await message.answer(
        "✅ Распознано!\n\n"
        f"📍 {property_data['address']}\n"
        f"🏷 Кадастр: {property_data['cadastral']}\n"
        f"📐 Площадь: {property_data['area']} м²\n\n"
        "💰 Шаг 4/6: Цена\n"
        "Введите цену квартиры (в рублях):\n"
        "Например: 12500000",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(Text(equals="📷 Загрузить ЕГРН"), state=DealStates.property_info)
async def property_upload_btn(message: types.Message, state: FSMContext):
    """Кнопка загрузки ЕГРН"""
    await message.answer(
        "📷 Пришлите фото выписки ЕГРН",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("◀️ Назад")
    )

@dp.message_handler(Text(equals="◀️ Назад"), state=DealStates.property_info)
async def property_back(message: types.Message, state: FSMContext):
    """Назад к покупателю"""
    await DealStates.buyer_passport.set()
    await message.answer(
        "👤 Шаг 2/6: Покупатель\n"
        "Пришлите фото паспорта покупателя",
        reply_markup=back_kb()
    )

@dp.message_handler(content_types=['text'], state=DealStates.property_info)
async def property_text(message: types.Message, state: FSMContext):
    """Ручной ввод адреса"""
    property_data = {
        "address": message.text,
        "cadastral": "77:04:0002017:4567",
        "area": 52.5
    }

    await state.update_data(property=property_data)
    await DealStates.price.set()

    await message.answer(
        "✅ Адрес сохранён!\n\n"
        "💰 Шаг 4/6: Цена\n"
        "Введите цену квартиры (в рублях):\n"
        "Например: 12500000",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ═══════════════════════════════════════════════════════════════
# ШАГ 4: ЦЕНА
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(content_types=['text'], state=DealStates.price)
async def price_input(message: types.Message, state: FSMContext):
    """Ввод цены"""
    try:
        price = int(message.text.replace(" ", "").replace("₽", "").replace(",", ""))
        advance = int(price * 0.04)  # 4% аванс
        main = price - advance

        await state.update_data(price={
            "total": price,
            "advance": advance,
            "main": main
        })

        await DealStates.escrow.set()
        await message.answer(
            f"💰 Цена: {format_price(price)} ₽\n"
            f"💡 Аванс (4%): {format_price(advance)} ₽\n"
            f"💡 Основной платёж: {format_price(main)} ₽\n\n"
            "Шаг 5/6: Выберите банк для эскроу",
            reply_markup=escrow_kb()
        )
    except ValueError:
        await message.answer(
            "❌ Введите число, например: 12500000\n"
            "Без пробелов, букв и символов валюты"
        )

# ═══════════════════════════════════════════════════════════════
# ШАГ 5: ЭСКРОУ
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(Text(equals="🏦 Сбербанк"), state=DealStates.escrow)
async def escrow_sber(message: types.Message, state: FSMContext):
    """Выбор Сбербанка"""
    await process_escrow(message, state, {
        "company": "ООО «Домклик»",
        "bank": "ПАО СБЕРБАНК РОССИИ",
        "bik": "044525225"
    })

@dp.message_handler(Text(equals="🏦 ВТБ"), state=DealStates.escrow)
async def escrow_vtb(message: types.Message, state: FSMContext):
    """Выбор ВТБ"""
    await process_escrow(message, state, {
        "company": "ООО «Домклик»",
        "bank": "ПАО ВТБ",
        "bik": "044525187"
    })

@dp.message_handler(Text(equals="🏦 Альфа-Банк"), state=DealStates.escrow)
async def escrow_alfa(message: types.Message, state: FSMContext):
    """Выбор Альфа-Банка"""
    await process_escrow(message, state, {
        "company": "ООО «Домклик»",
        "bank": "АО «АЛЬФА-БАНК»",
        "bik": "044525593"
    })

async def process_escrow(message, state, escrow_data):
    """Обработка выбора банка"""
    await state.update_data(escrow=escrow_data)
    await DealStates.validation.set()

    data = await state.get_data()
    seller = data.get('seller', {})
    buyer = data.get('buyer', {})
    property_data = data.get('property', {})
    price = data.get('price', {})

    await message.answer(
        "🔍 Шаг 6/6: Проверка данных\n\n"
        f"✅ Паспорт продавца — {seller.get('full_name', '—')}\n"
        f"✅ Паспорт покупателя — {buyer.get('full_name', '—')}\n"
        f"✅ Адрес — {property_data.get('address', '—')}\n"
        f"✅ Кадастр — {property_data.get('cadastral', '—')}\n"
        f"✅ Расчёты — {format_price(price.get('total', 0))} ₽ (сходится)\n"
        f"✅ Банк — {escrow_data['bank']}\n\n"
        "⚠️ Предупреждений: 0\n"
        "❌ Ошибок: 0\n\n"
        "Генерировать договор?",
        reply_markup=validation_kb()
    )

@dp.message_handler(Text(equals="✏️ Другой"), state=DealStates.escrow)
async def escrow_other(message: types.Message, state: FSMContext):
    """Другой банк"""
    await message.answer(
        "Введите название банка и БИК в формате:\n"
        "Название;БИК\n"
        "Пример: ПАО Газпромбанк;044525823",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(Text(equals="◀️ Назад"), state=DealStates.escrow)
async def escrow_back(message: types.Message, state: FSMContext):
    """Назад к цене"""
    await DealStates.price.set()
    await message.answer(
        "💰 Шаг 4/6: Цена\n"
        "Введите цену квартиры (в рублях):",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(content_types=['text'], state=DealStates.escrow)
async def escrow_custom(message: types.Message, state: FSMContext):
    """Обработка произвольного банка"""
    parts = message.text.split(";")
    if len(parts) >= 2:
        escrow_data = {
            "company": "ООО «Домклик»",
            "bank": parts[0].strip(),
            "bik": parts[1].strip()
        }
        await process_escrow(message, state, escrow_data)
    else:
        await message.answer(
            "❌ Неверный формат. Введите:\n"
            "Название банка;БИК"
        )

# ═══════════════════════════════════════════════════════════════
# ШАГ 6: ВАЛИДАЦИЯ И ГЕНЕРАЦИЯ
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(Text(equals="📄 Сгенерировать ДКП"), state=DealStates.validation)
async def generate_dkp(message: types.Message, state: FSMContext):
    """Генерация договора"""
    data = await state.get_data()

    await message.answer("📄 Генерирую договор...")

    # Имитация генерации
    await message.answer(
        "🎉 Договор готов!\n\n"
        "📄 DKP-2026-0043.pdf (245 KB)\n\n"
        "Содержит:\n"
        "• Договор купли-продажи\n"
        "• Передаточный акт\n\n"
        "[📤 Отправить сторонам]\n"
        "[💾 Сохранить в облаке]\n"
        "[📋 Мои сделки]",
        reply_markup=main_kb()
    )
    await DealStates.menu.set()

@dp.message_handler(Text(equals="✏️ Исправить данные"), state=DealStates.validation)
async def validation_edit(message: types.Message, state: FSMContext):
    """Исправление данных"""
    await message.answer(
        "Какие данные исправить?\n\n"
        "1 — Продавец\n"
        "2 — Покупатель\n"
        "3 — Объект\n"
        "4 — Цена\n"
        "5 — Банк\n\n"
        "Введите номер:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(Text(equals="◀️ Назад"), state=DealStates.validation)
async def validation_back(message: types.Message, state: FSMContext):
    """Назад к выбору банка"""
    await DealStates.escrow.set()
    await message.answer(
        "Шаг 5/6: Выберите банк для эскроу",
        reply_markup=escrow_kb()
    )

# ═══════════════════════════════════════════════════════════════
# FALLBACK
# ═══════════════════════════════════════════════════════════════

@dp.message_handler(state="*")
async def any_message(message: types.Message, state: FSMContext):
    """Обработка неожиданных сообщений"""
    current = await state.get_state()

    if current:
        await message.answer(
            f"❓ Я не понял команду в текущем режиме.\n"
            f"Текущий шаг: {current}\n\n"
            "Отправьте /start для перезапуска или /reset для сброса",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "👋 Для начала работы отправьте /start",
            reply_markup=types.ReplyKeyboardRemove()
        )

# ═══════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    logger.info("🤖 АвтоДКП Бот запущен!")
    logger.info("   Отправьте /start в Telegram")
    executor.start_polling(dp, skip_updates=True)
