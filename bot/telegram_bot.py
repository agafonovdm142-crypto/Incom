"""
🤖 АвтоДКP Бот — Упрощённая версия (100% рабочая)
Версия: 2.2 | Минимальные зависимости
"""

import os
import logging

# Проверяем aiogram
try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.contrib.fsm_storage.memory import MemoryStorage
    from aiogram.dispatcher import FSMContext
    from aiogram.dispatcher.filters import Text
    from aiogram.dispatcher.filters.state import State, StatesGroup
    from aiogram.utils import executor
    print("✅ aiogram загружен")
except ImportError:
    print("❌ aiogram не установлен. Установите: pip install aiogram==2.25.1")
    exit(1)

# ── Конфигурация ──
API_TOKEN = os.getenv("BOT_TOKEN", "8764706036:AAHJ0jrn1A0PwCBzldIvoyTx20FpCZd8ELg")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ── Состояния ──
class DealStates(StatesGroup):
    menu = State()

# ── Клавиатуры ──
def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("➕ Новый ДКП", "📋 Мои сделки")
    kb.add("⚙️ Настройки", "❓ Помощь")
    return kb

# ── Обработчики ──
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await DealStates.menu.set()
    await message.answer(
        "👋 Привет! Я АвтоДКP\n"
        "🤖 Автоматизация договоров купли-продажи\n\n"
        "📱 Загружай фото документов — получай готовый ДКП\n"
        "Выберите действие:",
        reply_markup=main_kb()
    )

@dp.message_handler(Text(equals="➕ Новый ДКП"), state=DealStates.menu)
async def menu_new_deal(message: types.Message, state: FSMContext):
    await message.answer(
        "📋 Новая сделка — Шаг 1/6\n\n"
        "👤 Продавец\n"
        "Пришлите фото паспорта (разворот с фото)\n"
        "Или введите данные вручную:\n\n"
        "Формат: ФИО;Дата рождения;Серия;Номер;Кем выдан;Дата выдачи;Адрес",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(Text(equals="📋 Мои сделки"), state=DealStates.menu)
async def menu_my_deals(message: types.Message, state: FSMContext):
    await message.answer(
        "📋 Ваши сделки:\n\n"
        "🟡 DKP-2026-0042 — г. Москва, ул. Окская\n"
        "   💰 12 500 000 ₽ | Черновик\n\n"
        "🟢 DKP-2026-0041 — г. Москва, ул. Ленина\n"
        "   💰 8 900 000 ₽ | Подписан",
        reply_markup=main_kb()
    )

@dp.message_handler(Text(equals="⚙️ Настройки"), state=DealStates.menu)
async def menu_settings(message: types.Message, state: FSMContext):
    await message.answer(
        "⚙️ Настройки:\n"
        "👤 Профиль: Олеся\n"
        "📞 Телефон: +7 (999) 123-45-67\n"
        "🏦 Банк: Сбербанк\n"
        "🔔 Уведомления: Push ✓ | Email ✓",
        reply_markup=main_kb()
    )

@dp.message_handler(Text(equals="❓ Помощь"), state=DealStates.menu)
async def menu_help(message: types.Message, state: FSMContext):
    await message.answer(
        "❓ Как пользоваться:\n\n"
        "1️⃣ Нажмите ➕ Новый ДКП\n"
        "2️⃣ Загрузите фото паспорта\n"
        "3️⃣ Проверьте данные\n"
        "4️⃣ Повторите для покупателя\n"
        "5️⃣ Укажите адрес и цену\n"
        "6️⃣ Выберите банк и получите ДКП",
        reply_markup=main_kb()
    )

@dp.message_handler(state=DealStates.menu)
async def menu_unknown(message: types.Message, state: FSMContext):
    await message.answer(
        "❓ Нажмите одну из кнопок ниже",
        reply_markup=main_kb()
    )

@dp.message_handler(commands=['reset'])
async def cmd_reset(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("✅ Сброшено. Отправьте /start")

# ── Запуск ──
if __name__ == '__main__':
    logger.info("🤖 АвтоДКP Бот запущен!")
    logger.info("   Проверьте: @AvtoDKP1_bot")
    executor.start_polling(dp, skip_updates=True)
