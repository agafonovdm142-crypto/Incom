
"""
🔍 OCR-Агент — распознавание документов для АвтоДКП
Поддерживает: паспорта РФ, СНИЛС, ИНН, выписки ЕГРН, банковские реквизиты
"""

import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple

@dataclass
class ExtractedDocument:
    doc_type: str  # passport, snils, inn, egrn, bank_requisites
    confidence: float
    fields: Dict[str, str]
    raw_text: str
    warnings: List[str]


class OCRAgent:
    """Агент распознавания документов"""

    def __init__(self, lang='rus+eng'):
        self.lang = lang
        self.confidence_threshold = 0.7

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Предобработка изображения для лучшего OCR"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Увеличение резкости
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)

        # Бинаризация
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Удаление шума
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

        return denoised

    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """Извлечение текста из изображения"""
        processed = self.preprocess_image(image_path)

        # OCR с confidence score
        data = pytesseract.image_to_data(processed, lang=self.lang, output_type=pytesseract.Output.DICT)

        text_parts = []
        confidences = []

        for i, text in enumerate(data['text']):
            if int(data['conf'][i]) > 30:  # Фильтр по confidence
                text_parts.append(text)
                confidences.append(int(data['conf'][i]))

        full_text = ' '.join(text_parts)
        avg_confidence = np.mean(confidences) if confidences else 0

        return full_text, avg_confidence / 100.0

    def detect_document_type(self, text: str) -> str:
        """Определение типа документа по тексту"""
        text_lower = text.lower()

        if 'паспорт' in text_lower and ('российской федерации' in text_lower or 'федерации' in text_lower):
            return 'passport'
        elif 'снилс' in text_lower or 'страховое свидетельство' in text_lower:
            return 'snils'
        elif 'инн' in text_lower or 'налогоплательщика' in text_lower:
            return 'inn'
        elif 'егрн' in text_lower or 'единый государственный реестр' in text_lower:
            return 'egrn'
        elif 'бик' in text_lower or 'расчетный счет' in text_lower or 'корреспондентский' in text_lower:
            return 'bank_requisites'
        elif 'свидетельство о праве' in text_lower or 'собственности' in text_lower:
            return 'ownership_certificate'
        else:
            return 'unknown'

    def extract_passport(self, text: str) -> Dict[str, str]:
        """Извлечение полей из паспорта РФ"""
        fields = {}
        warnings = []

        # ФИО — ищем паттерн "Фамилия Имя Отчество"
        name_patterns = [
            r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)',
            r'Фамилия[:\s]+([А-ЯЁ][а-яё]+).*Имя[:\s]+([А-ЯЁ][а-яё]+).*Отчество[:\s]+([А-ЯЁ][а-яё]+)'
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 1:
                    fields['full_name'] = match.group(1).strip()
                else:
                    fields['full_name'] = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                break

        if 'full_name' not in fields:
            warnings.append("Не удалось распознать ФИО")

        # Дата рождения
        birth_patterns = [
            r'(?:дата рождения|родился|родилась)[:\s]+(\d{2}\.\d{2}\.\d{4})',
            r'(\d{2}\.\d{2}\.\d{4})\s*(?:г\.р\.|года рождения)'
        ]

        for pattern in birth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['birth_date'] = match.group(1)
                break

        # Серия и номер паспорта
        passport_pattern = r'(\d{2}\s*\d{2})\s*(\d{6,7})'
        match = re.search(passport_pattern, text)
        if match:
            fields['passport_series'] = match.group(1).replace(' ', '')
            fields['passport_number'] = match.group(2)

        # Код подразделения
        dept_pattern = r'(\d{3}-\d{3})'
        match = re.search(dept_pattern, text)
        if match:
            fields['passport_dept_code'] = match.group(1)

        # Дата выдачи
        issue_pattern = r'(?:выдан|дата выдачи)[:\s]+(\d{2}\.\d{2}\.\d{4})'
        match = re.search(issue_pattern, text, re.IGNORECASE)
        if match:
            fields['passport_issued_date'] = match.group(1)

        # Кем выдан (берём текст после "выдан" до даты)
        issued_by_pattern = r'выдан[:\s]+(.+?)(?:\d{2}\.\d{2}\.\d{4})'
        match = re.search(issued_by_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            issued_by = match.group(1).strip()
            # Очищаем от лишних пробелов и переносов
            issued_by = re.sub(r'\s+', ' ', issued_by)
            fields['passport_issued_by'] = issued_by

        # Адрес регистрации
        address_patterns = [
            r'(?:зарегистрирован|прописан|адрес)[:\s]+(.+?)(?:\n|$)',
            r'(?:место жительства|жительства)[:\s]+(.+?)(?:\n|$)'
        ]

        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                address = match.group(1).strip()
                address = re.sub(r'\s+', ' ', address)
                fields['registration_address'] = address
                break

        return fields, warnings

    def extract_snils(self, text: str) -> Dict[str, str]:
        """Извлечение СНИЛС"""
        fields = {}
        warnings = []

        # СНИЛС: 123-456-789-01 или 12345678901
        snils_pattern = r'(\d{3}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{2})'
        match = re.search(snils_pattern, text)
        if match:
            snils = re.sub(r'\D', '', match.group(1))
            if len(snils) == 11:
                fields['snils'] = f"{snils[:3]}-{snils[3:6]}-{snils[6:9]}-{snils[9:11]}"
            else:
                warnings.append(f"СНИЛС неверной длины: {len(snils)} цифр")

        # ФИО (если есть)
        name_match = re.search(r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)', text)
        if name_match:
            fields['full_name'] = name_match.group(1)

        return fields, warnings

    def extract_inn(self, text: str) -> Dict[str, str]:
        """Извлечение ИНН"""
        fields = {}
        warnings = []

        # ИНН физлица: 12 цифр
        inn_pattern = r'(\d{12})'
        match = re.search(inn_pattern, text)
        if match:
            inn = match.group(1)
            # Проверка контрольной суммы
            if self._check_inn_checksum(inn):
                fields['inn'] = inn
            else:
                warnings.append("ИНН: контрольная сумма не совпадает")

        return fields, warnings

    def extract_egrn(self, text: str) -> Dict[str, str]:
        """Извлечение данных из выписки ЕГРН"""
        fields = {}
        warnings = []

        # Кадастровый номер
        cadastral_pattern = r'(\d{2}:\d{2}:\d{7}:\d+)'
        match = re.search(cadastral_pattern, text)
        if match:
            fields['cadastral_number'] = match.group(1)

        # Адрес
        address_pattern = r'(?:адрес|местоположение)[:\s]+(.+?)(?:\n|кадастровый)'
        match = re.search(address_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            fields['address'] = match.group(1).strip()

        # Площадь
        area_pattern = r'(\d+[.,]?\d*)\s*(?:кв\.м|м2|кв\.м\.)'
        match = re.search(area_pattern, text, re.IGNORECASE)
        if match:
            fields['area'] = match.group(1).replace(',', '.')

        # Собственник
        owner_pattern = r'(?:собственник|правообладатель)[:\s]+([А-ЯЁ][а-яё\s]+)'
        match = re.search(owner_pattern, text, re.IGNORECASE)
        if match:
            fields['owner'] = match.group(1).strip()

        return fields, warnings

    def extract_bank_requisites(self, text: str) -> Dict[str, str]:
        """Извлечение банковских реквизитов"""
        fields = {}

        # БИК
        bik_pattern = r'БИК[:\s]+(\d{9})'
        match = re.search(bik_pattern, text, re.IGNORECASE)
        if match:
            fields['bik'] = match.group(1)

        # Р/с
        rs_pattern = r'(?:р/с|расчетный счет)[:\s]+(\d{20})'
        match = re.search(rs_pattern, text, re.IGNORECASE)
        if match:
            fields['rs'] = match.group(1)

        # К/с
        ks_pattern = r'(?:к/с|корр\. счет)[:\s]+(\d{20})'
        match = re.search(ks_pattern, text, re.IGNORECASE)
        if match:
            fields['ks'] = match.group(1)

        # ИНН банка
        inn_pattern = r'ИНН[:\s]+(\d{10})'
        match = re.search(inn_pattern, text, re.IGNORECASE)
        if match:
            fields['inn'] = match.group(1)

        # Название банка
        bank_pattern = r'(ПАО\s+[А-ЯЁ\s]+|АО\s+[А-ЯЁ\s]+|ОАО\s+[А-ЯЁ\s]+)'
        match = re.search(bank_pattern, text)
        if match:
            fields['bank_name'] = match.group(1).strip()

        return fields, []

    def _check_inn_checksum(self, inn: str) -> bool:
        """Проверка контрольной суммы ИНН"""
        if len(inn) != 12:
            return False

        weights1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        weights2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]

        check1 = sum(int(inn[i]) * weights1[i] for i in range(10)) % 11 % 10
        check2 = sum(int(inn[i]) * weights2[i] for i in range(11)) % 11 % 10

        return int(inn[10]) == check1 and int(inn[11]) == check2

    def process_document(self, image_path: str) -> ExtractedDocument:
        """Главный метод: обработка документа от загрузки до результата"""
        # 1. Извлечение текста
        raw_text, confidence = self.extract_text(image_path)

        # 2. Определение типа документа
        doc_type = self.detect_document_type(raw_text)

        # 3. Извлечение полей по типу
        extractors = {
            'passport': self.extract_passport,
            'snils': self.extract_snils,
            'inn': self.extract_inn,
            'egrn': self.extract_egrn,
            'bank_requisites': self.extract_bank_requisites
        }

        extractor = extractors.get(doc_type, lambda x: ({}, ["Неизвестный тип документа"]))
        fields, warnings = extractor(raw_text)

        # 4. Дополнительные проверки
        if confidence < self.confidence_threshold:
            warnings.append(f"Низкая уверенность распознавания: {confidence:.1%}")

        return ExtractedDocument(
            doc_type=doc_type,
            confidence=confidence,
            fields=fields,
            raw_text=raw_text,
            warnings=warnings
        )


# ── ПРИМЕР ИСПОЛЬЗОВАНИЯ ──
if __name__ == "__main__":
    agent = OCRAgent()

    # Обработка паспорта
    result = agent.process_document("passport_photo.jpg")

    print(f"Тип документа: {result.doc_type}")
    print(f"Уверенность: {result.confidence:.1%}")
    print(f"Извлечённые поля:")
    for key, value in result.fields.items():
        print(f"  {key}: {value}")

    if result.warnings:
        print(f"⚠️ Предупреждения:")
        for warning in result.warnings:
            print(f"  - {warning}")
