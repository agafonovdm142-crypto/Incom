"""
⚙️ АвтоДКP Core — Ядро системы
Синхронизация данных между ботом и веб-приложением
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Person:
    full_name: str
    birth_date: str
    passport_series: str = ""
    passport_number: str = ""
    passport_issued_by: str = ""
    passport_issued_date: str = ""
    registration_address: str = ""
    inn: str = ""
    snils: str = ""

@dataclass
class Property:
    address: str
    cadastral: str
    area: float
    floor: int = 1
    rooms: int = 1
    type: str = "Квартира"

@dataclass
class Price:
    total: int
    advance: int
    main_payment: int

@dataclass
class Escrow:
    company: str
    bank: str
    bik: str

@dataclass
class Deal:
    id: str
    status: str
    date: str
    seller: Person
    buyer: Person
    property: Property
    price: Price
    escrow: Escrow
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

class DealStorage:
    """Хранилище сделок (в памяти + JSON)"""

    def __init__(self, filepath: str = "deals.json"):
        self.filepath = filepath
        self.deals: Dict[str, Deal] = {}
        self._load()

    def _load(self):
        """Загрузка из JSON"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for deal_id, deal_data in data.items():
                    self.deals[deal_id] = self._dict_to_deal(deal_data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save(self):
        """Сохранение в JSON"""
        data = {deal_id: self._deal_to_dict(deal) for deal_id, deal in self.deals.items()}
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _deal_to_dict(self, deal: Deal) -> dict:
        return {
            "id": deal.id,
            "status": deal.status,
            "date": deal.date,
            "seller": asdict(deal.seller),
            "buyer": asdict(deal.buyer),
            "property": asdict(deal.property),
            "price": asdict(deal.price),
            "escrow": asdict(deal.escrow),
            "created_at": deal.created_at,
            "updated_at": deal.updated_at
        }

    def _dict_to_deal(self, data: dict) -> Deal:
        return Deal(
            id=data["id"],
            status=data["status"],
            date=data["date"],
            seller=Person(**data["seller"]),
            buyer=Person(**data["buyer"]),
            property=Property(**data["property"]),
            price=Price(**data["price"]),
            escrow=Escrow(**data["escrow"]),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )

    def create_deal(self, seller: Person, buyer: Person, property: Property, 
                    price: Price, escrow: Escrow) -> Deal:
        """Создание новой сделки"""
        deal_id = f"DKP-{datetime.now().year}-{len(self.deals) + 1:04d}"
        deal = Deal(
            id=deal_id,
            status="draft",
            date=datetime.now().strftime("%d.%m.%Y"),
            seller=seller,
            buyer=buyer,
            property=property,
            price=price,
            escrow=escrow
        )
        self.deals[deal_id] = deal
        self._save()
        return deal

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Получить сделку по ID"""
        return self.deals.get(deal_id)

    def list_deals(self, status: Optional[str] = None) -> List[Deal]:
        """Список сделок (с фильтром по статусу)"""
        deals = list(self.deals.values())
        if status:
            deals = [d for d in deals if d.status == status]
        return sorted(deals, key=lambda x: x.created_at, reverse=True)

    def update_deal(self, deal_id: str, **kwargs) -> Optional[Deal]:
        """Обновление сделки"""
        deal = self.deals.get(deal_id)
        if deal:
            for key, value in kwargs.items():
                if hasattr(deal, key):
                    setattr(deal, key, value)
            deal.updated_at = datetime.now().isoformat()
            self._save()
        return deal

    def delete_deal(self, deal_id: str) -> bool:
        """Удаление сделки"""
        if deal_id in self.deals:
            del self.deals[deal_id]
            self._save()
            return True
        return False

class ValidationService:
    """Сервис валидации данных"""

    @staticmethod
    def validate_passport(series: str, number: str) -> tuple:
        """Валидация паспорта РФ"""
        errors = []
        if not series or len(series.replace(" ", "")) != 4:
            errors.append("Серия паспорта должна содержать 4 цифры")
        if not number or len(number) != 6:
            errors.append("Номер паспорта должен содержать 6 цифр")
        return (len(errors) == 0, errors)

    @staticmethod
    def validate_inn(inn: str) -> tuple:
        """Валидация ИНН (контрольная сумма)"""
        if len(inn) != 12:
            return (False, ["ИНН должен содержать 12 цифр"])

        weights1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        weights2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]

        check1 = sum(int(inn[i]) * weights1[i] for i in range(10)) % 11 % 10
        check2 = sum(int(inn[i]) * weights2[i] for i in range(11)) % 11 % 10

        if int(inn[10]) == check1 and int(inn[11]) == check2:
            return (True, [])
        return (False, ["Контрольная сумма ИНН не совпадает"])

    @staticmethod
    def validate_price(total: int, advance: int, main: int) -> tuple:
        """Валидация расчётов"""
        errors = []
        if total <= 0:
            errors.append("Цена должна быть больше 0")
        if advance + main != total:
            errors.append(f"Аванс + Основной ≠ Цена ({advance:,} + {main:,} ≠ {total:,})")
        if advance < total * 0.01:
            errors.append("Аванс слишком мал (минимум 1%)")
        return (len(errors) == 0, errors)

    @staticmethod
    def validate_cadastral(cadastral: str) -> tuple:
        """Валидация кадастрового номера"""
        parts = cadastral.split(":")
        if len(parts) != 4:
            return (False, ["Кадастровый номер должен иметь формат XX:XX:XXXXXXX:X"])
        return (True, [])

class ContractGenerator:
    """Генератор договора"""

    TEMPLATE = """
ДОГОВОР КУПЛИ-ПРОДАЖИ КВАРТИРЫ

г. Москва                                                                               {date}

    {seller_name}, {seller_type} РФ, паспорт {seller_passport}, выдан {seller_issued},
    зарегистрированный по адресу: {seller_address},
    именуемый в дальнейшем «Продавец», с одной стороны, и

    {buyer_name}, {buyer_type} РФ, паспорт {buyer_passport}, выдан {buyer_issued},
    зарегистрированный по адресу: {buyer_address},
    именуемый в дальнейшем «Покупатель», с другой стороны,

    совместно именуемые «Стороны», заключили настоящий договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Продавец продаёт, а Покупатель покупает квартиру:
    - Адрес: {property_address}
    - Кадастровый номер: {property_cadastral}
    - Площадь: {property_area} м²

2. ЦЕНА И ПОРЯДОК РАСЧЁТОВ

2.1. Общая цена: {price_total} ({price_total_words}) рублей 00 копеек.

2.2. Аванс (задаток): {price_advance} руб.
    Основной платёж: {price_main} руб.

2.3. Расчёты производятся через эскроу:
    - {escrow_company}
    - Банк: {escrow_bank}
    - БИК: {escrow_bik}

3. ПРАВА И ОБЯЗАННОСТИ СТОРОН

3.1. Продавец обязуется передать квартиру в течение 30 дней.
3.2. Покупатель обязуется оплатить полную стоимость до регистрации.

4. ПОДПИСИ СТОРОН

    _________________ / {seller_name} /          _________________ / {buyer_name} /
           (Подпись)                                                   (Подпись)
"""

    @staticmethod
    def generate(deal: Deal) -> str:
        """Генерация текста договора"""
        return ContractGenerator.TEMPLATE.format(
            date=deal.date,
            seller_name=deal.seller.full_name,
            seller_type="гражданин" if "ич" in deal.seller.full_name else "гражданка",
            seller_passport=f"{deal.seller.passport_series} №{deal.seller.passport_number}",
            seller_issued=deal.seller.passport_issued_by,
            seller_address=deal.seller.registration_address,
            buyer_name=deal.buyer.full_name,
            buyer_type="гражданин" if "ич" in deal.buyer.full_name else "гражданка",
            buyer_passport=f"{deal.buyer.passport_series} №{deal.buyer.passport_number}",
            buyer_issued=deal.buyer.passport_issued_by,
            buyer_address=deal.buyer.registration_address,
            property_address=deal.property.address,
            property_cadastral=deal.property.cadastral,
            property_area=deal.property.area,
            price_total=f"{deal.price.total:,}".replace(",", " "),
            price_total_words="двенадцать миллионов пятьсот тысяч",  # TODO: num2words
            price_advance=f"{deal.price.advance:,}".replace(",", " "),
            price_main=f"{deal.price.main_payment:,}".replace(",", " "),
            escrow_company=deal.escrow.company,
            escrow_bank=deal.escrow.bank,
            escrow_bik=deal.escrow.bik
        )

# ── ПРИМЕР ИСПОЛЬЗОВАНИЯ ──
if __name__ == "__main__":
    storage = DealStorage()

    # Создаём тестовую сделку
    deal = storage.create_deal(
        seller=Person(
            full_name="Петров Петр Петрович",
            birth_date="15.03.1985",
            passport_series="45 06",
            passport_number="123456"
        ),
        buyer=Person(
            full_name="Иванов Иван Иванович",
            birth_date="22.07.1990",
            passport_series="40 02",
            passport_number="654321"
        ),
        property=Property(
            address="г. Москва, ул. Окская, д. 36, корп. 4, кв. 45",
            cadastral="77:04:0002017:4567",
            area=52.5
        ),
        price=Price(total=12500000, advance=500000, main_payment=12000000),
        escrow=Escrow(company="ООО «Домклик»", bank="ПАО СБЕРБАНК РОССИИ", bik="044525225")
    )

    print(f"Создана сделка: {deal.id}")

    # Генерация договора
    contract = ContractGenerator.generate(deal)
    print("\n" + "="*50)
    print(contract)

    # Валидация
    validator = ValidationService()
    ok, errors = validator.validate_passport(deal.seller.passport_series, deal.seller.passport_number)
    print(f"\nВалидация паспорта: {'✅' if ok else '❌'}")
    if errors:
        print("Ошибки:", errors)
