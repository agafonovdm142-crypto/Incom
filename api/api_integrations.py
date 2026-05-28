
"""
🌐 API-Интеграции — проверка данных через государственные сервисы
ФНС, Росреестр, ЕГРН, ГИС ГМП (проверка задолженностей)
"""

import requests
import json
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime

@dataclass
class APIResult:
    service: str
    status: str  # ok, error, timeout, unavailable
    data: Dict
    errors: List[str]
    response_time_ms: int


class FNSAPI:
    """Проверка ИНН через API ФНС России"""

    BASE_URL = "https://api-fns.ru/api/"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def check_inn(self, inn: str) -> APIResult:
        """Проверка ИНН физического лица"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}inn",
                params={"inn": inn},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return APIResult(
                    service="ФНС (ИНН)",
                    status="ok",
                    data={
                        "inn": inn,
                        "valid": data.get("valid", False),
                        "full_name": data.get("name"),
                        "registration_date": data.get("registration_date")
                    },
                    errors=[],
                    response_time_ms=int(response.elapsed.total_seconds() * 1000)
                )
            else:
                return APIResult(
                    service="ФНС (ИНН)",
                    status="error",
                    data={},
                    errors=[f"HTTP {response.status_code}: {response.text}"],
                    response_time_ms=0
                )

        except requests.Timeout:
            return APIResult(
                service="ФНС (ИНН)",
                status="timeout",
                data={},
                errors=["Превышено время ожидания ответа от ФНС"],
                response_time_ms=10000
            )
        except Exception as e:
            return APIResult(
                service="ФНС (ИНН)",
                status="unavailable",
                data={},
                errors=[str(e)],
                response_time_ms=0
            )

    def check_organization(self, inn: str) -> APIResult:
        """Проверка ИНН юридического лица (банк, эскроу)"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}org",
                params={"inn": inn},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return APIResult(
                    service="ФНС (Организация)",
                    status="ok",
                    data={
                        "inn": inn,
                        "name": data.get("name"),
                        "ogrn": data.get("ogrn"),
                        "address": data.get("address"),
                        "status": data.get("status", "active")
                    },
                    errors=[],
                    response_time_ms=int(response.elapsed.total_seconds() * 1000)
                )
            else:
                return APIResult(
                    service="ФНС (Организация)",
                    status="error",
                    data={},
                    errors=[f"HTTP {response.status_code}"],
                    response_time_ms=0
                )
        except Exception as e:
            return APIResult(
                service="ФНС (Организация)",
                status="unavailable",
                data={},
                errors=[str(e)],
                response_time_ms=0
            )


class RosreestrAPI:
    """Проверка кадастровых номеров через API Росреестра"""

    BASE_URL = "https://rosreestr.gov.ru/api/online"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()

    def check_cadastral(self, cadastral_number: str) -> APIResult:
        """Проверка кадастрового номера"""
        try:
            # Росреестр имеет открытый API для проверки
            response = self.session.get(
                f"{self.BASE_URL}/features/{cadastral_number}",
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                # Проверка на аресты и обременения
                restrictions = data.get("restrictions", [])
                encumbrances = data.get("encumbrances", [])

                errors = []
                if restrictions:
                    errors.append(f"⚠️ Найдены ограничения: {len(restrictions)}")
                if encumbrances:
                    errors.append(f"⚠️ Найдены обременения: {len(encumbrances)}")

                return APIResult(
                    service="Росреестр (Кадастр)",
                    status="ok",
                    data={
                        "cadastral_number": cadastral_number,
                        "address": data.get("address"),
                        "area": data.get("area"),
                        "type": data.get("type"),
                        "owner": data.get("owner"),
                        "restrictions_count": len(restrictions),
                        "encumbrances_count": len(encumbrances),
                        "has_issues": bool(restrictions or encumbrances)
                    },
                    errors=errors,
                    response_time_ms=int(response.elapsed.total_seconds() * 1000)
                )

            elif response.status_code == 404:
                return APIResult(
                    service="Росреестр (Кадастр)",
                    status="error",
                    data={},
                    errors=["Кадастровый номер не найден в реестре"],
                    response_time_ms=int(response.elapsed.total_seconds() * 1000)
                )
            else:
                return APIResult(
                    service="Росреестр (Кадастр)",
                    status="error",
                    data={},
                    errors=[f"HTTP {response.status_code}"],
                    response_time_ms=0
                )

        except requests.Timeout:
            return APIResult(
                service="Росреестр (Кадастр)",
                status="timeout",
                data={},
                errors=["Превышено время ожидания ответа от Росреестра"],
                response_time_ms=15000
            )
        except Exception as e:
            return APIResult(
                service="Росреестр (Кадастр)",
                status="unavailable",
                data={},
                errors=[str(e)],
                response_time_ms=0
            )

    def get_egrn_extract(self, cadastral_number: str) -> APIResult:
        """Заказ и получение выписки ЕГРН"""
        try:
            # API для заказа выписки (платная услуга)
            response = self.session.post(
                f"{self.BASE_URL}/order/extract",
                json={"cadastral_number": cadastral_number},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return APIResult(
                    service="Росреестр (ЕГРН)",
                    status="ok",
                    data={
                        "order_id": data.get("order_id"),
                        "status": "ordered",
                        "estimated_time": "1-3 рабочих дня",
                        "cost": 350  # руб.
                    },
                    errors=[],
                    response_time_ms=int(response.elapsed.total_seconds() * 1000)
                )
            else:
                return APIResult(
                    service="Росреестр (ЕГРН)",
                    status="error",
                    data={},
                    errors=[f"HTTP {response.status_code}"],
                    response_time_ms=0
                )
        except Exception as e:
            return APIResult(
                service="Росреестр (ЕГРН)",
                status="unavailable",
                data={},
                errors=[str(e)],
                response_time_ms=0
            )


class GISGMPAPI:
    """Проверка задолженностей через ГИС ГМП"""

    BASE_URL = "https://www.gosuslugi.ru/api/gisgmp"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}"
        })

    def check_debts(self, inn: str, address: str) -> APIResult:
        """Проверка задолженностей по ЖКХ, налогам, штрафам"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/debts",
                params={"inn": inn, "address": address},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                debts = data.get("debts", [])

                total_debt = sum(d.get("amount", 0) for d in debts)

                errors = []
                if total_debt > 0:
                    errors.append(f"⚠️ Обнаружена задолженность: {total_debt:,} руб.")

                return APIResult(
                    service="ГИС ГМП (Задолженности)",
                    status="ok",
                    data={
                        "inn": inn,
                        "total_debt": total_debt,
                        "debts_count": len(debts),
                        "debts_details": debts,
                        "has_debts": total_debt > 0
                    },
                    errors=errors,
                    response_time_ms=int(response.elapsed.total_seconds() * 1000)
                )
            else:
                return APIResult(
                    service="ГИС ГМП (Задолженности)",
                    status="error",
                    data={},
                    errors=[f"HTTP {response.status_code}"],
                    response_time_ms=0
                )
        except Exception as e:
            return APIResult(
                service="ГИС ГМП (Задолженности)",
                status="unavailable",
                data={},
                errors=[str(e)],
                response_time_ms=0
            )


class ValidationOrchestrator:
    """Оркестратор: запускает все проверки параллельно"""

    def __init__(self, fns_key: Optional[str] = None, 
                 rosreestr_key: Optional[str] = None,
                 gisgmp_key: Optional[str] = None):
        self.fns = FNSAPI(fns_key) if fns_key else None
        self.rosreestr = RosreestrAPI(rosreestr_key)
        self.gisgmp = GISGMPAPI(gisgmp_key) if gisgmp_key else None

    def validate_deal(self, deal_data: Dict) -> Dict:
        """Полная проверка сделки через все доступные API"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "warnings": 0,
                "errors": 0
            }
        }

        seller = deal_data.get("seller", {})
        buyer = deal_data.get("buyer", {})
        property_data = deal_data.get("property", {})
        escrow = deal_data.get("escrow", {})

        # 1. Проверка ИНН продавца
        if self.fns and seller.get("inn"):
            result = self.fns.check_inn(seller["inn"])
            results["checks"].append(self._format_result(result))

        # 2. Проверка ИНН покупателя
        if self.fns and buyer.get("inn"):
            result = self.fns.check_inn(buyer["inn"])
            results["checks"].append(self._format_result(result))

        # 3. Проверка ИНН эскроу-компании
        if self.fns and escrow.get("inn"):
            result = self.fns.check_organization(escrow["inn"])
            results["checks"].append(self._format_result(result))

        # 4. Проверка кадастрового номера
        if property_data.get("cadastral_number"):
            result = self.rosreestr.check_cadastral(property_data["cadastral_number"])
            results["checks"].append(self._format_result(result))

        # 5. Проверка задолженностей продавца
        if self.gisgmp and seller.get("inn") and seller.get("registration_address"):
            result = self.gisgmp.check_debts(seller["inn"], seller["registration_address"])
            results["checks"].append(self._format_result(result))

        # Подсчёт статистики
        for check in results["checks"]:
            results["summary"]["total"] += 1
            if check["status"] == "ok" and not check["has_issues"]:
                results["summary"]["passed"] += 1
            elif check["has_issues"]:
                results["summary"]["warnings"] += 1
            elif check["status"] in ["error", "timeout", "unavailable"]:
                results["summary"]["errors"] += 1

        return results

    def _format_result(self, result: APIResult) -> Dict:
        """Форматирование результата для ответа"""
        return {
            "service": result.service,
            "status": result.status,
            "data": result.data,
            "errors": result.errors,
            "response_time_ms": result.response_time_ms,
            "has_issues": bool(result.errors)
        }


# ── ПРИМЕР ИСПОЛЬЗОВАНИЯ ──
if __name__ == "__main__":
    # Без API-ключей (демо-режим)
    orchestrator = ValidationOrchestrator()

    deal = {
        "seller": {
            "inn": "123456789012",
            "registration_address": "г. Москва, ул. Сокольнический вал, д. 10, кв. 45"
        },
        "buyer": {
            "inn": "987654321098"
        },
        "property": {
            "cadastral_number": "77:04:0002017:4567"
        },
        "escrow": {
            "inn": "7736249247"
        }
    }

    results = orchestrator.validate_deal(deal)

    print(f"Проверка завершена: {results['summary']['total']} проверок")
    print(f"  ✅ Пройдено: {results['summary']['passed']}")
    print(f"  ⚠️ Предупреждения: {results['summary']['warnings']}")
    print(f"  ❌ Ошибки: {results['summary']['errors']}")
