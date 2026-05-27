"""
🌐 backend.py — Единый сервер АвтоДКP
Синхронизация: телефон ↔ компьютер ↔ облако
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import threading
import time

# Хранилище сделок (в памяти + автосохранение в JSON)
DEALS_FILE = "deals_db.json"
_lock = threading.Lock()

@dataclass
class SyncDeal:
    """Сделка с метаданными синхронизации"""
    deal_id: str
    user_id: str
    status: str  # draft, phone_partial, pc_partial, complete, generated

    # Данные (можут быть частичными)
    seller_name: str = ""
    seller_passport: str = ""
    seller_birth_date: str = ""
    seller_address: str = ""
    seller_inn: str = ""

    buyer_name: str = ""
    buyer_passport: str = ""
    buyer_birth_date: str = ""
    buyer_address: str = ""
    buyer_inn: str = ""

    property_address: str = ""
    property_cadastral: str = ""
    property_area: float = 0.0
    property_type: str = "Квартира"

    price_total: int = 0
    price_advance: int = 0
    price_main: int = 0

    bank_name: str = ""
    bank_bik: str = ""
    escrow_company: str = ""

    # Метаданные
    created_from: str = ""  # phone, pc, web
    last_modified: str = ""
    last_device: str = ""   # phone, pc
    completion_percent: int = 0

    # OCR данные
    ocr_seller_photo: str = ""  # base64 или путь
    ocr_buyer_photo: str = ""
    ocr_egrn_photo: str = ""

    # Документы
    contract_text: str = ""
    contract_generated: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "SyncDeal":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class DealStorage:
    """Хранилище сделок с автосохранением"""

    def __init__(self):
        self.deals: Dict[str, SyncDeal] = {}
        self._load()

    def _load(self):
        """Загрузка из файла"""
        if os.path.exists(DEALS_FILE):
            try:
                with open(DEALS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for deal_id, deal_data in data.items():
                        self.deals[deal_id] = SyncDeal.from_dict(deal_data)
                print(f"📂 Загружено {len(self.deals)} сделок")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки: {e}")

    def _save(self):
        """Сохранение в файл"""
        with _lock:
            try:
                data = {deal_id: deal.to_dict() for deal_id, deal in self.deals.items()}
                with open(DEALS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ Ошибка сохранения: {e}")

    def create(self, user_id: str, device: str) -> SyncDeal:
        """Создание новой сделки"""
        deal_id = f"DKP-{user_id}-{int(time.time())}"
        deal = SyncDeal(
            deal_id=deal_id,
            user_id=user_id,
            status="draft",
            created_from=device,
            last_device=device,
            last_modified=datetime.now().isoformat(),
            completion_percent=0
        )
        self.deals[deal_id] = deal
        self._save()
        return deal

    def get(self, deal_id: str) -> Optional[SyncDeal]:
        """Получение сделки"""
        return self.deals.get(deal_id)

    def update(self, deal_id: str, fields: Dict, device: str) -> Optional[SyncDeal]:
        """Обновление сделки"""
        deal = self.deals.get(deal_id)
        if not deal:
            return None

        # Обновляем поля
        for key, value in fields.items():
            if hasattr(deal, key):
                setattr(deal, key, value)

        deal.last_device = device
        deal.last_modified = datetime.now().isoformat()
        deal.completion_percent = self._calculate_completion(deal)

        # Автоопределение статуса
        if deal.completion_percent >= 100:
            deal.status = "complete"
        elif deal.completion_percent > 50:
            deal.status = "pc_partial" if device == "pc" else "phone_partial"

        self._save()
        return deal

    def _calculate_completion(self, deal: SyncDeal) -> int:
        """Расчёт процента заполнения"""
        fields = [
            deal.seller_name, deal.seller_passport,
            deal.buyer_name, deal.buyer_passport,
            deal.property_address, deal.property_cadastral,
            deal.price_total, deal.bank_name
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

    def list_user_deals(self, user_id: str) -> List[SyncDeal]:
        """Список сделок пользователя"""
        return [d for d in self.deals.values() if d.user_id == user_id]

    def generate_contract(self, deal_id: str) -> Optional[str]:
        """Генерация договора"""
        deal = self.deals.get(deal_id)
        if not deal or deal.completion_percent < 80:
            return None

        contract = f"""
ДОГОВОР КУПЛИ-ПРОДАЖИ {deal.property_type.upper()}

г. Москва

1. ПРЕДМЕТ ДОГОВОРА
Продавец: {deal.seller_name}, паспорт {deal.seller_passport}
Покупатель: {deal.buyer_name}, паспорт {deal.buyer_passport}

Объект: {deal.property_type}, {deal.property_area} м²
Адрес: {deal.property_address}
Кадастровый номер: {deal.property_cadastral}

2. ЦЕНА
{deal.price_total:,} ({deal.price_total:,}) рублей 00 копеек
Аванс: {deal.price_advance:,} руб.
Основной платёж: {deal.price_main:,} руб.

3. РАСЧЁТЫ ЧЕРЕЗ ЭСКРОУ
{deal.escrow_company}
Банк: {deal.bank_name}
БИК: {deal.bank_bik}

4. ПОДПИСИ
Продавец: _________________ / {deal.seller_name.split()[0] if deal.seller_name else ""} /
Покупатель: _________________ / {deal.buyer_name.split()[0] if deal.buyer_name else ""} /
"""

        deal.contract_text = contract
        deal.contract_generated = True
        deal.status = "generated"
        self._save()

        return contract


# ═══════════════════════════════════════════════════════════════
# API для Telegram бота и Web
# ═══════════════════════════════════════════════════════════════

class DealAPI:
    """API для работы с сделками"""

    def __init__(self):
        self.storage = DealStorage()

    def create_deal(self, user_id: str, device: str) -> Dict:
        """Создать сделку"""
        deal = self.storage.create(user_id, device)
        return {
            "status": "ok",
            "deal_id": deal.deal_id,
            "completion": 0,
            "message": "Сделка создана. Заполняйте с любого устройства."
        }

    def update_field(self, deal_id: str, field: str, value, device: str) -> Dict:
        """Обновить одно поле"""
        deal = self.storage.update(deal_id, {field: value}, device)
        if not deal:
            return {"status": "error", "message": "Сделка не найдена"}

        return {
            "status": "ok",
            "deal_id": deal_id,
            "field": field,
            "completion": deal.completion_percent,
            "status_text": deal.status,
            "message": self._get_progress_message(deal)
        }

    def get_status(self, deal_id: str) -> Dict:
        """Получить статус сделки"""
        deal = self.storage.get(deal_id)
        if not deal:
            return {"status": "error", "message": "Сделка не найдена"}

        missing = self._get_missing_fields(deal)

        return {
            "status": "ok",
            "deal_id": deal_id,
            "completion": deal.completion_percent,
            "status": deal.status,
            "last_device": deal.last_device,
            "missing_fields": missing,
            "can_generate": deal.completion_percent >= 80,
            "contract_generated": deal.contract_generated
        }

    def generate(self, deal_id: str) -> Dict:
        """Генерировать договор"""
        contract = self.storage.generate_contract(deal_id)
        if not contract:
            deal = self.storage.get(deal_id)
            missing = self._get_missing_fields(deal) if deal else []
            return {
                "status": "error",
                "message": "Недостаточно данных",
                "missing": missing,
                "completion": deal.completion_percent if deal else 0
            }

        return {
            "status": "ok",
            "deal_id": deal_id,
            "contract": contract,
            "message": "Договор сгенерирован!"
        }

    def _get_progress_message(self, deal: SyncDeal) -> str:
        """Сообщение о прогрессе"""
        if deal.completion_percent == 0:
            return "Начните заполнять данные"
        elif deal.completion_percent < 30:
            return f"Заполнено {deal.completion_percent}%. Продолжайте!"
        elif deal.completion_percent < 60:
            return f"Заполнено {deal.completion_percent}%. Половина готова!"
        elif deal.completion_percent < 100:
            missing = self._get_missing_fields(deal)
            return f"Заполнено {deal.completion_percent}%. Осталось: {', '.join(missing[:3])}"
        else:
            return "✅ Все данные собраны! Можно генерировать договор."

    def _get_missing_fields(self, deal: SyncDeal) -> List[str]:
        """Список незаполненных полей"""
        required = {
            "Продавец (ФИО)": deal.seller_name,
            "Паспорт продавца": deal.seller_passport,
            "Покупатель (ФИО)": deal.buyer_name,
            "Паспорт покупателя": deal.buyer_passport,
            "Адрес объекта": deal.property_address,
            "Кадастровый номер": deal.property_cadastral,
            "Цена": deal.price_total,
            "Банк": deal.bank_name
        }
        return [name for name, value in required.items() if not value]


# ═══════════════════════════════════════════════════════════════
# СИНХРОНИЗАЦИЯ МЕЖДУ УСТРОЙСТВАМИ
# ═══════════════════════════════════════════════════════════════

class SyncManager:
    """Менеджер синхронизации между телефоном и компьютером"""

    def __init__(self, api: DealAPI):
        self.api = api

    def sync_check(self, user_id: str, current_device: str) -> Dict:
        """Проверить, есть ли данные с другого устройства"""
        deals = self.api.storage.list_user_deals(user_id)

        # Ищем незавершённые сделки с другого устройства
        other_device_deals = [
            d for d in deals 
            if d.last_device != current_device and d.status in ["draft", "phone_partial", "pc_partial"]
        ]

        if other_device_deals:
            deal = other_device_deals[-1]  # Последняя
            return {
                "has_sync_data": True,
                "deal_id": deal.deal_id,
                "from_device": deal.last_device,
                "completion": deal.completion_percent,
                "message": f"📱 Найдена сделка с {deal.last_device} ({deal.completion_percent}%). Продолжить?",
                "missing": self.api._get_missing_fields(deal)
            }

        return {"has_sync_data": False}

    def get_continue_prompt(self, deal_id: str) -> str:
        """Получить подсказку что заполнять дальше"""
        deal = self.api.storage.get(deal_id)
        if not deal:
            return "Сделка не найдена"

        missing = self.api._get_missing_fields(deal)

        if not missing:
            return "✅ Все данные собраны! Нажмите 'Сгенерировать договор'"

        # Группируем по категориям
        groups = {
            "seller": [m for m in missing if "продавец" in m.lower() or "Продавец" in m],
            "buyer": [m for m in missing if "покупатель" in m.lower() or "Покупатель" in m],
            "property": [m for m in missing if "адрес" in m.lower() or "кадастр" in m.lower()],
            "money": [m for m in missing if "цена" in m.lower() or "банк" in m.lower()]
        }

        msg = "📋 Что заполнить дальше:

"
        for group_name, items in groups.items():
            if items:
                emoji = {"seller": "👤", "buyer": "👤", "property": "🏠", "money": "💰"}.get(group_name, "📌")
                msg += f"{emoji} {', '.join(items)}
"

        return msg


# ═══════════════════════════════════════════════════════════════
# ЗАПУСК СЕРВЕРА (для локального использования)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🌐 АвтоДКP Backend запущен")
    print("   Хранилище сделок активно")
    print("   Файл: deals_db.json")

    # Тест
    api = DealAPI()
    result = api.create_deal("user_123", "phone")
    print(f"
✅ Тест: создана сделка {result['deal_id']}")
