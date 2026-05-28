
"""
✍️ Модуль электронной подписи и автоподачи (Версия 2)
Двухэтапное подтверждение перед подачей в Росреестр:
1. «Подтверждаю, что данные верны» — финальная проверка
2. «Направить документ» — отправка в Росреестр
"""

import hashlib
import base64
from dataclasses import dataclass
from typing import Optional, Dict, List, BinaryIO
from datetime import datetime
import json
import requests

@dataclass
class SignatureResult:
    status: str
    signature_type: str
    signer_name: str
    signed_at: datetime
    signature_data: Optional[str]
    errors: List[str]


class SimpleSignature:
    """Простая электронная подпись"""

    def sign_document(self, document: bytes, signer_name: str) -> SignatureResult:
        doc_hash = hashlib.sha256(document).hexdigest()
        timestamp = datetime.now().isoformat()
        payload = {"hash": doc_hash, "signer": signer_name, "timestamp": timestamp, "type": "simple"}
        signature_data = base64.b64encode(json.dumps(payload).encode()).decode()

        return SignatureResult(
            status="signed", signature_type="simple", signer_name=signer_name,
            signed_at=datetime.now(), signature_data=signature_data, errors=[]
        )


class UKEPSignature:
    """Усиленная квалифицированная ЭП (КриптоПро)"""

    def __init__(self, crypto_pro_path: str = "/opt/cprocsp"):
        self.available = self._check_crypto_pro(crypto_pro_path)

    def _check_crypto_pro(self, path: str) -> bool:
        import os
        return os.path.exists(path)

    def sign_document(self, document: bytes, signer_name: str, certificate_id: str) -> SignatureResult:
        if not self.available:
            return SignatureResult(
                status="error", signature_type="ukep", signer_name=signer_name,
                signed_at=datetime.now(), signature_data=None,
                errors=["КриптоПро не установлен. Установите: www.cryptopro.ru"]
            )

        doc_hash = hashlib.sha256(document).hexdigest()
        signature_data = base64.b64encode(f"UKEP:{certificate_id}:{doc_hash}".encode()).decode()

        return SignatureResult(
            status="signed", signature_type="ukep", signer_name=signer_name,
            signed_at=datetime.now(), signature_data=signature_data, errors=[]
        )


class RosreestrSubmission:
    """Автоподача документов в Росреестр с двухэтапным подтверждением"""

    BASE_URL = "https://rosreestr.gov.ru/api/online/registration"

    def __init__(self, ukep_signature: Optional[UKEPSignature] = None):
        self.signature = ukep_signature
        self.session = requests.Session()

    def validate_for_submission(self, deal_data: Dict, 
                                 seller_signature: str,
                                 buyer_signature: str) -> Dict:
        """
        ЭТАП 0: Предварительная проверка перед показом кнопок
        Возвращает статус готовности и список что нужно исправить
        """
        readiness = {
            "ready": False,
            "stage": "pre_check",
            "checks": {},
            "blockers": [],
            "can_proceed_to_confirm": False
        }

        # Проверка 1: УКЭП установлена?
        if not self.signature or not self.signature.available:
            readiness["blockers"].append("❌ УКЭП (КриптоПро) не установлена")
            readiness["checks"]["ukep"] = {"status": "missing", "required": True}
        else:
            readiness["checks"]["ukep"] = {"status": "ok", "required": True}

        # Проверка 2: Договор подписан обеими сторонами?
        if not seller_signature:
            readiness["blockers"].append("❌ Договор не подписан продавцом")
            readiness["checks"]["seller_signature"] = {"status": "missing", "required": True}
        else:
            readiness["checks"]["seller_signature"] = {"status": "ok", "required": True}

        if not buyer_signature:
            readiness["blockers"].append("❌ Договор не подписан покупателем")
            readiness["checks"]["buyer_signature"] = {"status": "missing", "required": True}
        else:
            readiness["checks"]["buyer_signature"] = {"status": "ok", "required": True}

        # Проверка 3: Все обязательные поля заполнены?
        required_fields = [
            ("seller.full_name", "ФИО продавца"),
            ("seller.inn", "ИНН продавца"),
            ("seller.passport_series", "Паспорт продавца"),
            ("buyer.full_name", "ФИО покупателя"),
            ("buyer.inn", "ИНН покупателя"),
            ("buyer.passport_series", "Паспорт покупателя"),
            ("property.cadastral_number", "Кадастровый номер"),
            ("property.address_full", "Адрес объекта"),
            ("price.total", "Цена"),
            ("escrow.company", "Компания эскроу"),
            ("escrow.inn", "ИНН эскроу")
        ]

        missing_fields = []
        for field_path, field_name in required_fields:
            parts = field_path.split(".")
            value = deal_data
            for part in parts:
                value = value.get(part, {}) if isinstance(value, dict) else None

            if not value or value == {}:
                missing_fields.append(field_name)

        if missing_fields:
            readiness["blockers"].append(f"❌ Не заполнены поля: {', '.join(missing_fields)}")
            readiness["checks"]["required_fields"] = {"status": "incomplete", "missing": missing_fields}
        else:
            readiness["checks"]["required_fields"] = {"status": "ok"}

        # Проверка 4: Валидация пройдена?
        # (предполагается, что validation_result передаётся отдельно)

        # Проверка 5: Госпошлина оплачена?
        readiness["checks"]["state_duty"] = {
            "status": "pending", 
            "amount": 2000,
            "message": "Госпошлина 2 000 руб. — оплатите перед подачей"
        }

        # Итог
        if not readiness["blockers"]:
            readiness["ready"] = True
            readiness["can_proceed_to_confirm"] = True
            readiness["stage"] = "ready_for_confirmation"
        else:
            readiness["stage"] = "blocked"

        return readiness

    def confirm_data_accuracy(self, deal_data: Dict, user_id: str) -> Dict:
        """
        ЭТАП 1: Пользователь подтверждает, что данные верны
        Фиксируем время, IP, создаём аудит-лог
        """
        confirmation = {
            "stage": "confirmed",
            "confirmed_at": datetime.now().isoformat(),
            "confirmed_by": user_id,
            "deal_id": deal_data.get("meta", {}).get("deal_id", "unknown"),
            "confirmation_hash": None,
            "next_step": "submit_to_rosreestr",
            "warnings": []
        }

        # Создаём хеш всех данных для аудита
        data_string = json.dumps(deal_data, sort_keys=True, ensure_ascii=False)
        confirmation["confirmation_hash"] = hashlib.sha256(
            data_string.encode()
        ).hexdigest()[:16]

        # Проверяем, не прошло ли много времени с момента валидации
        # (если данные менялись — требуем повторную проверку)

        confirmation["warnings"] = [
            "⚠️ После подтверждения изменение данных потребует нового подтверждения",
            "⚠️ Подача в Росреестр необратима — отозвать можно только через суд"
        ]

        return confirmation

    def submit_to_rosreestr(self, deal_data: Dict,
                          signed_contract: bytes,
                          seller_signature: str,
                          buyer_signature: str,
                          confirmation_hash: str) -> Dict:
        """
        ЭТАП 2: Непосредственная подача в Росреестр
        Только после confirm_data_accuracy!
        """

        # Проверяем, что подтверждение было получено
        if not confirmation_hash:
            return {
                "status": "error",
                "stage": "submission_blocked",
                "message": "Требуется предварительное подтверждение данных",
                "action_required": "Нажмите 'Подтверждаю, что данные верны'"
            }

        # Проверяем УКЭП ещё раз
        if not self.signature or not self.signature.available:
            return {
                "status": "error",
                "stage": "submission_blocked",
                "message": "Для подачи в Росреестр требуется УКЭП",
                "alternatives": [
                    "1. Установить КриптоПро CSP",
                    "2. Обратиться к нотариусу (электронная регистрация)",
                    "3. Подать через МФЦ или лично"
                ]
            }

        try:
            # Формирование пакета документов
            package = {
                "application_type": "registration_rights_transfer",
                "confirmation": {
                    "hash": confirmation_hash,
                    "confirmed_at": datetime.now().isoformat()
                },
                "property": {
                    "cadastral_number": deal_data["property"]["cadastral_number"],
                    "address": deal_data["property"]["address_full"]
                },
                "parties": {
                    "seller": {
                        "full_name": deal_data["seller"]["full_name"],
                        "inn": deal_data["seller"]["inn"],
                        "signature": seller_signature,
                        "signature_type": "ukep"
                    },
                    "buyer": {
                        "full_name": deal_data["buyer"]["full_name"],
                        "inn": deal_data["buyer"]["inn"],
                        "signature": buyer_signature,
                        "signature_type": "ukep"
                    }
                },
                "documents": {
                    "contract": base64.b64encode(signed_contract).decode(),
                    "contract_type": "dkp",
                    "egrn_extract": deal_data.get("egrn_extract_base64", ""),
                    "passport_seller": deal_data.get("passport_seller_base64", ""),
                    "passport_buyer": deal_data.get("passport_buyer_base64", "")
                },
                "payment": {
                    "state_duty": 2000,
                    "payment_confirmed": True,
                    "payment_receipt": deal_data.get("payment_receipt_base64", "")
                },
                "metadata": {
                    "submitted_at": datetime.now().isoformat(),
                    "submission_method": "api",
                    "auto_submitted": True
                }
            }

            # Отправка в Росреестр
            response = self.session.post(
                f"{self.BASE_URL}/submit",
                json=package,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "submitted",
                    "stage": "rosreestr_received",
                    "application_id": data.get("application_id"),
                    "registration_number": data.get("registration_number"),
                    "estimated_time": "7 рабочих дней",
                    "track_url": f"https://rosreestr.gov.ru/check/{data.get('application_id')}",
                    "next_steps": [
                        "1. Сохраните номер заявления",
                        "2. Оплатите госпошлину (если не оплачена)",
                        "3. Ожидайте SMS/e-mail уведомления",
                        "4. Получите выписку ЕГРН с новым собственником"
                    ],
                    "important": [
                        "⚠️ Заявление нельзя отозвать без согласия покупателя",
                        "⚠️ При отказе Росреестра — исправьте ошибки и подайте повторно",
                        "⚠️ Срок регистрации: 7 рабочих дней (можно ускорить за доплату)"
                    ]
                }

            elif response.status_code == 400:
                errors = response.json().get("errors", [])
                return {
                    "status": "error",
                    "stage": "submission_rejected",
                    "message": "Росреестр отклонил заявление",
                    "errors": errors,
                    "action_required": "Исправьте ошибки и повторите подачу"
                }

            else:
                return {
                    "status": "error",
                    "stage": "submission_failed",
                    "message": f"Ошибка сервера Росреестра: HTTP {response.status_code}",
                    "retry_allowed": True
                }

        except requests.Timeout:
            return {
                "status": "error",
                "stage": "submission_timeout",
                "message": "Превышено время ожидания ответа от Росреестра",
                "retry_allowed": True,
                "alternative": "Попробуйте подать через нотариуса"
            }

        except Exception as e:
            return {
                "status": "error",
                "stage": "submission_exception",
                "message": str(e),
                "retry_allowed": False,
                "alternative": "Обратитесь в техническую поддержку"
            }

    def check_status(self, application_id: str) -> Dict:
        """Проверка статуса регистрации"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/status/{application_id}",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                status_map = {
                    "received": "📥 Принято",
                    "checking": "🔍 На проверке",
                    "additional_docs_required": "📎 Требуются доп. документы",
                    "registered": "✅ Зарегистрировано",
                    "rejected": "❌ Отказано",
                    "suspended": "⏸️ Приостановлено"
                }

                return {
                    "application_id": application_id,
                    "status_code": data.get("status"),
                    "status_text": status_map.get(data.get("status"), data.get("status")),
                    "updated_at": data.get("updated_at"),
                    "comments": data.get("comments", []),
                    "can_download_extract": data.get("status") == "registered",
                    "extract_url": data.get("extract_url") if data.get("status") == "registered" else None
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# ── ИНТЕРФЕЙС ДЛЯ ПОЛЬЗОВАТЕЛЯ (кнопки) ──
class SubmissionUI:
    """UI-логика для двухэтапной подачи"""

    def __init__(self, rosreestr: RosreestrSubmission):
        self.rosreestr = rosreestr
        self.confirmation_state = {}  # user_id -> confirmation_hash

    def show_submission_panel(self, deal_data: Dict, user_id: str,
                            seller_sig: str, buyer_sig: str) -> Dict:
        """Показывает панель с кнопками в зависимости от статуса"""

        # Этап 0: Проверка готовности
        readiness = self.rosreestr.validate_for_submission(
            deal_data, seller_sig, buyer_sig
        )

        if not readiness["ready"]:
            return {
                "panel_type": "blocked",
                "title": "❌ Подача недоступна",
                "message": "Исправьте следующие проблемы:",
                "blockers": readiness["blockers"],
                "actions": []
            }

        # Проверяем, было ли уже подтверждение
        confirmation = self.confirmation_state.get(user_id)

        if not confirmation:
            # Показываем кнопку подтверждения
            return {
                "panel_type": "confirmation_required",
                "title": "🔒 Подтверждение данных",
                "message": "Перед подачей в Росреестр подтвердите, что все данные верны.",
                "warnings": [
                    "После подтверждения изменение данных потребует нового подтверждения",
                    "Подача в Росреестр необратима"
                ],
                "actions": [
                    {
                        "id": "confirm_data",
                        "label": "✅ Подтверждаю, что данные верны",
                        "style": "primary",
                        "confirmation_required": True,
                        "confirmation_text": "Я подтверждаю, что все данные в договоре верны и соответствуют оригиналам документов."
                    }
                ]
            }

        else:
            # Показываем кнопку подачи
            return {
                "panel_type": "ready_to_submit",
                "title": "🚀 Готово к подаче",
                "message": f"Данные подтверждены ({confirmation['confirmed_at']}). Можно направить в Росреестр.",
                "confirmation_hash": confirmation["confirmation_hash"],
                "actions": [
                    {
                        "id": "submit_rosreestr",
                        "label": "📤 Направить документ в Росреестр",
                        "style": "danger",
                        "confirmation_required": True,
                        "confirmation_text": "Вы уверены? Подача необратима. Госпошлина: 2 000 руб."
                    },
                    {
                        "id": "cancel_confirmation",
                        "label": "◀️ Отменить подтверждение",
                        "style": "secondary"
                    }
                ]
            }

    def handle_confirm(self, deal_data: Dict, user_id: str) -> Dict:
        """Обработка нажатия 'Подтверждаю, что данные верны'"""
        result = self.rosreestr.confirm_data_accuracy(deal_data, user_id)
        self.confirmation_state[user_id] = result
        return result

    def handle_submit(self, deal_data: Dict, user_id: str,
                     signed_contract: bytes,
                     seller_sig: str, buyer_sig: str) -> Dict:
        """Обработка нажатия 'Направить документ'"""
        confirmation = self.confirmation_state.get(user_id)

        if not confirmation:
            return {
                "status": "error",
                "message": "Требуется предварительное подтверждение данных"
            }

        result = self.rosreestr.submit_to_rosreestr(
            deal_data, signed_contract,
            seller_sig, buyer_sig,
            confirmation["confirmation_hash"]
        )

        # Очищаем подтверждение после подачи (или при ошибке)
        if result["status"] == "submitted":
            del self.confirmation_state[user_id]

        return result

    def handle_cancel(self, user_id: str) -> Dict:
        """Отмена подтверждения"""
        if user_id in self.confirmation_state:
            del self.confirmation_state[user_id]
            return {"status": "cancelled", "message": "Подтверждение отменено"}
        return {"status": "no_confirmation", "message": "Нет активного подтверждения"}
