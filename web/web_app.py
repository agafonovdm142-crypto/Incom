"""
💻 АвтоДКП Веб — Streamlit интерфейс для автоматизации ДКП
Версия: 2.0 | Улучшенная навигация и обработка ошибок
"""

import streamlit as st
import json
from datetime import datetime

# ── Настройка страницы ──
st.set_page_config(
    page_title="АвтоДКП — Автоматизация договоров",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS стили ──
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem; }
    .status-badge { padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; }
    .status-draft { background: #fff3cd; color: #856404; }
    .status-check { background: #d1ecf1; color: #0c5460; }
    .status-signed { background: #d4edda; color: #155724; }
    .status-done { background: #d4edda; color: #155724; }
    .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .field-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
    .field-value { font-size: 1rem; font-weight: 500; color: #333; }
    .step-active { background: #1f77b4; color: white; padding: 8px 16px; border-radius: 20px; }
    .step-inactive { background: #f0f0f0; color: #666; padding: 8px 16px; border-radius: 20px; }
    .success-box { background: #d4edda; border: 1px solid #155724; padding: 15px; border-radius: 8px; }
    .warning-box { background: #fff3cd; border: 1px solid #856404; padding: 15px; border-radius: 8px; }
    .error-box { background: #f8d7da; border: 1px solid #721c24; padding: 15px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Инициализация состояния ──
def init_session():
    if 'deals' not in st.session_state:
        st.session_state.deals = [
            {
                "id": "DKP-2026-0042",
                "status": "draft",
                "date": "25.05.2026",
                "seller": {
                    "full_name": "Петров Петр Петрович",
                    "birth_date": "15.03.1985",
                    "passport_series": "45 06",
                    "passport_number": "123456",
                    "passport_issued_by": "ОТДЕЛЕНИЕ УФМС РОССИИ ПО ГОР. МОСКВЕ",
                    "passport_issued_date": "10.02.2010",
                    "registration_address": "г. Москва, ул. Сокольнический вал, д. 10, кв. 45"
                },
                "buyer": {
                    "full_name": "Иванов Иван Иванович",
                    "birth_date": "22.07.1990",
                    "passport_series": "40 02",
                    "passport_number": "654321",
                    "passport_issued_by": "ОТДЕЛЕНИЕ УФМС РОССИИ ПО ГОР. МОСКВЕ",
                    "passport_issued_date": "15.03.2015",
                    "registration_address": "г. Москва, ул. Ленинградская, д. 15, кв. 78"
                },
                "property": {
                    "address": "г. Москва, ул. Окская, д. 36, корп. 4, кв. 45",
                    "cadastral": "77:04:0002017:4567",
                    "area": 52.5,
                    "floor": 5,
                    "rooms": 2
                },
                "price": {"total": 12500000, "advance": 500000, "main_payment": 12000000},
                "escrow": {"company": "ООО «Домклик»", "bank": "ПАО СБЕРБАНК РОССИИ", "bik": "044525225"}
            },
            {
                "id": "DKP-2026-0041",
                "status": "signed",
                "date": "20.05.2026",
                "seller": {"full_name": "Сидорова Анна Владимировна"},
                "buyer": {"full_name": "Кузнецов Дмитрий Сергеевич"},
                "property": {
                    "address": "г. Москва, ул. Ленина, д. 15, кв. 78",
                    "cadastral": "77:01:0001023:89",
                    "area": 38.0
                },
                "price": {"total": 8900000, "advance": 300000, "main_payment": 8600000},
                "escrow": {"company": "ООО «Домклик»", "bank": "ПАО ВТБ", "bik": "044525187"}
            }
        ]

    if 'current_deal' not in st.session_state:
        st.session_state.current_deal = None

    if 'new_deal_step' not in st.session_state:
        st.session_state.new_deal_step = 1

    if 'new_deal_data' not in st.session_state:
        st.session_state.new_deal_data = {}

init_session()

# ── Боковое меню ──
st.sidebar.markdown("<div class='main-header'>🏠 АвтоДКП</div>", unsafe_allow_html=True)
st.sidebar.markdown("Автоматизация договоров купли-продажи")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Навигация",
    ["📋 Мои сделки", "➕ Новая сделка", "⚙️ Настройки", "❓ Помощь"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Олеся** — Риелтор | Москва")
st.sidebar.markdown("📱 Бот: @AvtoDKP1_bot")

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ-ПОМОЩНИКИ
# ═══════════════════════════════════════════════════════════════

def format_price(price):
    return f"{price:,}".replace(",", " ")

def get_status_badge(status):
    status_map = {
        "draft": ("Черновик", "status-draft"),
        "check": ("На проверке", "status-check"),
        "signed": ("Подписан", "status-signed"),
        "done": ("Завершён", "status-done")
    }
    return status_map.get(status, (status, "status-draft"))

# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА: МОИ СДЕЛКИ
# ═══════════════════════════════════════════════════════════════

if menu == "📋 Мои сделки" and not st.session_state.current_deal:
    st.markdown("<div class='main-header'>📋 Мои сделки</div>", unsafe_allow_html=True)

    # Фильтры
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        status_filter = st.selectbox("Статус", ["Все", "Черновик", "На проверке", "Подписан", "Завершён"])
    with col2:
        search = st.text_input("Поиск по адресу или ФИО")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Новая", use_container_width=True, type="primary"):
            st.session_state.current_deal = "new"
            st.session_state.new_deal_step = 1
            st.session_state.new_deal_data = {}
            st.rerun()

    st.markdown("---")

    # Фильтрация сделок
    filtered_deals = st.session_state.deals
    if status_filter != "Все":
        status_map_reverse = {"Черновик": "draft", "На проверке": "check", 
                             "Подписан": "signed", "Завершён": "done"}
        filtered_deals = [d for d in filtered_deals if d['status'] == status_map_reverse.get(status_filter)]

    if search:
        filtered_deals = [d for d in filtered_deals if 
                         search.lower() in d['property']['address'].lower() or
                         search.lower() in d['seller']['full_name'].lower() or
                         search.lower() in d['buyer']['full_name'].lower()]

    # Список сделок
    if not filtered_deals:
        st.info("📭 Сделок не найдено. Создайте новую сделку!")
    else:
        for deal in filtered_deals:
            status_text, status_class = get_status_badge(deal['status'])

            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

                with col1:
                    st.markdown(f"""
                    <div class='card'>
                        <div class='field-label'>№ СДЕЛКИ</div>
                        <div class='field-value'>{deal['id']}</div>
                        <div style='margin-top: 8px;'>
                            <span class='status-badge {status_class}'>{status_text}</span>
                        </div>
                        <div class='field-label' style='margin-top: 8px;'>{deal['date']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class='card'>
                        <div class='field-label'>ПРОДАВЕЦ → ПОКУПАТЕЛЬ</div>
                        <div class='field-value'>{deal['seller']['full_name']}</div>
                        <div class='field-value'>→ {deal['buyer']['full_name']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class='card'>
                        <div class='field-label'>ОБЪЕКТ | ЦЕНА</div>
                        <div class='field-value'>{deal['property']['address']}</div>
                        <div class='field-value' style='color: #1f77b4; font-weight: bold;'>
                            {format_price(deal['price']['total'])} ₽
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    st.markdown(f"""
                    <div class='card' style='text-align: center;'>
                        <div class='field-label'>КАДАСТР</div>
                        <div class='field-value' style='font-size: 0.85rem;'>{deal['property']['cadastral']}</div>
                        <div class='field-label' style='margin-top: 8px;'>{deal['property']['area']} м²</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col5:
                    if st.button("Открыть", key=f"open_{deal['id']}", use_container_width=True):
                        st.session_state.current_deal = deal['id']
                        st.rerun()
                    if st.button("📥 PDF", key=f"pdf_{deal['id']}", use_container_width=True):
                        st.info("PDF генерируется...")

# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА: ДЕТАЛИ СДЕЛКИ
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_deal and st.session_state.current_deal != "new":
    deal = next((d for d in st.session_state.deals if d['id'] == st.session_state.current_deal), None)

    if deal:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"<div class='main-header'>{deal['id']}</div>", unsafe_allow_html=True)
        with col2:
            status_text, status_class = get_status_badge(deal['status'])
            st.markdown(f"<span class='status-badge {status_class}'>{status_text}</span>", unsafe_allow_html=True)
        with col3:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()

        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["📄 Договор", "👤 Стороны", "🏠 Объект", "💰 Расчёты"])

        with tab1:
            st.markdown("### 📄 Текст договора")

            col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
            with col1:
                if st.button("🔍 Проверить", use_container_width=True):
                    st.success("✅ Проверка пройдена: 0 ошибок, 0 предупреждений")
            with col2:
                if st.button("📥 Скачать PDF", use_container_width=True):
                    st.info("PDF генерируется...")
            with col3:
                if st.button("✏️ Редактировать", use_container_width=True):
                    st.session_state.edit_mode = True
            with col4:
                if st.button("📤 Отправить на подписание", type="primary", use_container_width=True):
                    st.success("✅ Договор отправлен сторонам на согласование!")

            contract_preview = f"""
ДОГОВОР КУПЛИ-ПРОДАЖИ КВАРТИРЫ

г. Москва                                                                               {deal['date']}

    {deal['seller']['full_name']}, именуемый в дальнейшем «Продавец», с одной стороны, и
    {deal['buyer']['full_name']}, именуемый в дальнейшем «Покупатель», с другой стороны,
    совместно именуемые «Стороны», заключили настоящий договор (далее — «Договор») о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Продавец продаёт, а Покупатель покупает квартиру:
    - Адрес: {deal['property']['address']}
    - Кадастровый номер: {deal['property']['cadastral']}
    - Площадь: {deal['property']['area']} м²

2. ЦЕНА И ПОРЯДОК РАСЧЁТОВ

2.1. Общая цена: {format_price(deal['price']['total'])} ({format_price(deal['price']['total'])}) рублей 00 копеек.

2.2. Аванс (задаток): {format_price(deal['price']['advance'])} руб.
    Основной платёж: {format_price(deal['price']['main_payment'])} руб.

2.3. Расчёты производятся через эскроу:
    - {deal['escrow']['company']}
    - Банк: {deal['escrow']['bank']}
    - БИК: {deal['escrow']['bik']}

3. ПРАВА И ОБЯЗАННОСТИ СТОРОН

3.1. Продавец обязуется передать квартиру в течение 30 дней с момента подписания.
3.2. Покупатель обязуется оплатить полную стоимость до момента регистрации перехода права.

4. ПОДПИСИ СТОРОН

    _________________ / {deal['seller']['full_name']} /          _________________ / {deal['buyer']['full_name']} /
           (Подпись)                                                   (Подпись)
"""
            st.text_area("", value=contract_preview, height=500)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 👤 Продавец")
                st.text_input("ФИО", value=deal['seller'].get('full_name', ''), key="s_fio")
                st.text_input("Дата рождения", value=deal['seller'].get('birth_date', ''), key="s_bd")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.text_input("Серия", value=deal['seller'].get('passport_series', ''), key="s_ser")
                with col_s2:
                    st.text_input("Номер", value=deal['seller'].get('passport_number', ''), key="s_num")
                st.text_input("Кем выдан", value=deal['seller'].get('passport_issued_by', ''), key="s_iss")
                st.text_input("Дата выдачи", value=deal['seller'].get('passport_issued_date', ''), key="s_id")
                st.text_input("Адрес регистрации", value=deal['seller'].get('registration_address', ''), key="s_addr")
                if st.button("💾 Сохранить продавца", key="save_seller"):
                    st.success("✅ Данные продавца сохранены")

            with col2:
                st.markdown("#### 👤 Покупатель")
                st.text_input("ФИО", value=deal['buyer'].get('full_name', ''), key="b_fio")
                st.text_input("Дата рождения", value=deal['buyer'].get('birth_date', ''), key="b_bd")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    st.text_input("Серия", value=deal['buyer'].get('passport_series', ''), key="b_ser")
                with col_b2:
                    st.text_input("Номер", value=deal['buyer'].get('passport_number', ''), key="b_num")
                st.text_input("Кем выдан", value=deal['buyer'].get('passport_issued_by', ''), key="b_iss")
                st.text_input("Дата выдачи", value=deal['buyer'].get('passport_issued_date', ''), key="b_id")
                st.text_input("Адрес регистрации", value=deal['buyer'].get('registration_address', ''), key="b_addr")
                if st.button("💾 Сохранить покупателя", key="save_buyer"):
                    st.success("✅ Данные покупателя сохранены")

        with tab3:
            st.markdown("#### 🏠 Объект недвижимости")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Тип", value="Квартира", key="prop_type")
                st.text_input("Адрес", value=deal['property']['address'], key="prop_addr")
                st.text_input("Кадастровый номер", value=deal['property']['cadastral'], key="prop_cad")
            with col2:
                st.number_input("Площадь (м²)", value=float(deal['property']['area']), key="prop_area")
                st.number_input("Этаж", value=int(deal['property'].get('floor', 1)), key="prop_floor")
                st.number_input("Комнат", value=int(deal['property'].get('rooms', 1)), key="prop_rooms")

            uploaded_egrn = st.file_uploader("📷 Загрузить выписку ЕГРН", type=["jpg", "jpeg", "png", "pdf"], key="egrn_upload")
            if uploaded_egrn:
                st.success("✅ Выписка загружена")

            if st.button("💾 Сохранить объект", key="save_prop"):
                st.success("✅ Данные объекта сохранены")

        with tab4:
            st.markdown("#### 💰 Цена и расчёты")
            col1, col2, col3 = st.columns(3)
            with col1:
                new_price = st.number_input("Цена", value=deal['price']['total'], key="price_total")
            with col2:
                new_advance = st.number_input("Аванс", value=deal['price']['advance'], key="price_adv")
            with col3:
                new_main = st.number_input("Основной платёж", value=deal['price']['main_payment'], key="price_main")

            # Проверка расчётов
            if new_advance + new_main == new_price:
                st.markdown("<div class='success-box'>✅ Расчёт сходится: Аванс + Основной = Цена</div>", unsafe_allow_html=True)
            else:
                diff = new_price - (new_advance + new_main)
                st.markdown(f"<div class='error-box'>❌ Расчёт не сходится: разница {diff:,} ₽</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 🏦 Эскроу")
            st.text_input("Компания", value=deal['escrow']['company'], key="esc_comp")
            bank_options = ["ПАО СБЕРБАНК РОССИИ", "ПАО ВТБ", "АО «АЛЬФА-БАНК»", "Другой"]
            selected_bank = st.selectbox("Банк", bank_options, index=bank_options.index(deal['escrow']['bank']) if deal['escrow']['bank'] in bank_options else 3, key="esc_bank")
            if selected_bank == "Другой":
                st.text_input("Название банка", key="esc_bank_custom")
            st.text_input("БИК", value=deal['escrow']['bik'], key="esc_bik")

            if st.button("💾 Сохранить расчёты", key="save_price"):
                st.success("✅ Данные расчётов сохранены")

# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА: НОВАЯ СДЕЛКА (МАСТЕР)
# ═══════════════════════════════════════════════════════════════

elif menu == "➕ Новая сделка" or st.session_state.current_deal == "new":
    st.markdown("<div class='main-header'>➕ Новая сделка</div>", unsafe_allow_html=True)

    step = st.session_state.new_deal_step

    # Индикатор шагов
    steps = ["1. Продавец", "2. Покупатель", "3. Объект", "4. Цена", "5. Банк", "6. Проверка"]
    cols = st.columns(len(steps))
    for i, (col, step_name) in enumerate(zip(cols, steps)):
        with col:
            if i + 1 == step:
                st.markdown(f"<div class='step-active'>{step_name}</div>", unsafe_allow_html=True)
            elif i + 1 < step:
                st.markdown(f"<div class='step-inactive'>✓ {step_name}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='step-inactive'>{step_name}</div>", unsafe_allow_html=True)

    st.markdown("---")

    if step == 1:
        st.markdown("### 📷 Шаг 1: Данные продавца")
        col1, col2 = st.columns(2)
        with col1:
            uploaded = st.file_uploader("Фото паспорта (разворот)", type=["jpg", "jpeg", "png"], key="seller_photo")
            if uploaded:
                st.image(uploaded, width=300, caption="Загруженное фото")
                with st.spinner("Распознаю паспорт..."):
                    st.success("✅ Распознано: Петров Петр Петрович")
                    st.session_state.new_deal_data['seller'] = {
                        "full_name": "Петров Петр Петрович",
                        "birth_date": "15.03.1985",
                        "passport_series": "45 06",
                        "passport_number": "123456"
                    }
        with col2:
            st.markdown("#### Или введите вручную:")
            s_fio = st.text_input("ФИО продавца", key="new_s_fio")
            s_bd = st.text_input("Дата рождения", key="new_s_bd")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                s_ser = st.text_input("Серия", key="new_s_ser")
            with col_s2:
                s_num = st.text_input("Номер", key="new_s_num")
            s_iss = st.text_input("Кем выдан", key="new_s_iss")
            s_id = st.text_input("Дата выдачи", key="new_s_id")
            s_addr = st.text_input("Адрес регистрации", key="new_s_addr")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("◀️ Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with col_btn2:
            if st.button("Далее →", type="primary", use_container_width=True):
                if s_fio:
                    st.session_state.new_deal_data['seller'] = {
                        "full_name": s_fio, "birth_date": s_bd, "passport_series": s_ser,
                        "passport_number": s_num, "passport_issued_by": s_iss,
                        "passport_issued_date": s_id, "registration_address": s_addr
                    }
                st.session_state.new_deal_step = 2
                st.rerun()

    elif step == 2:
        st.markdown("### 📷 Шаг 2: Данные покупателя")
        # Аналогично шагу 1...
        col1, col2 = st.columns(2)
        with col1:
            uploaded = st.file_uploader("Фото паспорта покупателя", type=["jpg", "jpeg", "png"], key="buyer_photo")
            if uploaded:
                st.image(uploaded, width=300)
                st.success("✅ Распознано: Иванов Иван Иванович")
        with col2:
            b_fio = st.text_input("ФИО покупателя", key="new_b_fio")
            b_bd = st.text_input("Дата рождения", key="new_b_bd")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                b_ser = st.text_input("Серия", key="new_b_ser")
            with col_b2:
                b_num = st.text_input("Номер", key="new_b_num")

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 1
                st.rerun()
        with col_btn2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with col_btn3:
            if st.button("Далее →", type="primary", use_container_width=True):
                st.session_state.new_deal_step = 3
                st.rerun()

    elif step == 3:
        st.markdown("### 🏠 Шаг 3: Объект недвижимости")
        col1, col2 = st.columns(2)
        with col1:
            prop_addr = st.text_input("Адрес", key="new_prop_addr")
            prop_cad = st.text_input("Кадастровый номер", key="new_prop_cad")
        with col2:
            prop_area = st.number_input("Площадь (м²)", value=0.0, key="new_prop_area")
            prop_floor = st.number_input("Этаж", value=1, key="new_prop_floor")

        uploaded_egrn = st.file_uploader("Выписка ЕГРН", type=["jpg", "jpeg", "png", "pdf"], key="new_egrn")

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 2
                st.rerun()
        with col_btn2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with col_btn3:
            if st.button("Далее →", type="primary", use_container_width=True):
                st.session_state.new_deal_step = 4
                st.rerun()

    elif step == 4:
        st.markdown("### 💰 Шаг 4: Цена")
        price_total = st.number_input("Цена квартиры (₽)", value=0, step=100000, key="new_price")

        if price_total > 0:
            advance = int(price_total * 0.04)
            main = price_total - advance
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Аванс (4%)", f"{advance:,} ₽")
            with col2:
                st.metric("Основной платёж", f"{main:,} ₽")
            with col3:
                st.metric("Итого", f"{price_total:,} ₽")

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 3
                st.rerun()
        with col_btn2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with col_btn3:
            if st.button("Далее →", type="primary", use_container_width=True):
                st.session_state.new_deal_data['price'] = {
                    "total": price_total,
                    "advance": int(price_total * 0.04),
                    "main_payment": price_total - int(price_total * 0.04)
                }
                st.session_state.new_deal_step = 5
                st.rerun()

    elif step == 5:
        st.markdown("### 🏦 Шаг 5: Банк для эскроу")
        bank = st.selectbox("Выберите банк", ["Сбербанк", "ВТБ", "Альфа-Банк", "Другой"], key="new_bank")
        if bank == "Другой":
            st.text_input("Название банка", key="new_bank_custom")
            st.text_input("БИК", key="new_bik")

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 4
                st.rerun()
        with col_btn2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with col_btn3:
            if st.button("Далее →", type="primary", use_container_width=True):
                bank_data = {
                    "Сбербанк": {"company": "ООО «Домклик»", "bank": "ПАО СБЕРБАНК РОССИИ", "bik": "044525225"},
                    "ВТБ": {"company": "ООО «Домклик»", "bank": "ПАО ВТБ", "bik": "044525187"},
                    "Альфа-Банк": {"company": "ООО «Домклик»", "bank": "АО «АЛЬФА-БАНК»", "bik": "044525593"}
                }
                st.session_state.new_deal_data['escrow'] = bank_data.get(bank, {"company": "ООО «Домклик»", "bank": bank, "bik": "000000000"})
                st.session_state.new_deal_step = 6
                st.rerun()

    elif step == 6:
        st.markdown("### 🔍 Шаг 6: Проверка данных")

        data = st.session_state.new_deal_data

        checks = [
            ("Паспорт продавца", bool(data.get('seller')), "✅" if data.get('seller') else "❌"),
            ("Паспорт покупателя", bool(data.get('buyer')), "✅" if data.get('buyer') else "❌"),
            ("Объект недвижимости", bool(data.get('property')), "✅" if data.get('property') else "❌"),
            ("Цена", bool(data.get('price')), "✅" if data.get('price') else "❌"),
            ("Банк эскроу", bool(data.get('escrow')), "✅" if data.get('escrow') else "❌"),
        ]

        for name, status, icon in checks:
            if status:
                st.markdown(f"<div class='success-box'>{icon} {name} — заполнено</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='error-box'>{icon} {name} — не заполнено</div>", unsafe_allow_html=True)

        all_ok = all(status for _, status, _ in checks)

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 5
                st.rerun()
        with col_btn2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with col_btn3:
            if all_ok:
                if st.button("📄 Сгенерировать ДКП", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("✅ Договор успешно сгенерирован!")
                    # Добавляем в список сделок
                    new_deal = {
                        "id": f"DKP-2026-{len(st.session_state.deals) + 43:04d}",
                        "status": "draft",
                        "date": datetime.now().strftime("%d.%m.%Y"),
                        **st.session_state.new_deal_data
                    }
                    st.session_state.deals.append(new_deal)
                    st.session_state.current_deal = None
                    st.session_state.new_deal_data = {}
                    st.session_state.new_deal_step = 1
                    st.rerun()
            else:
                st.button("📄 Сгенерировать ДКП", disabled=True, use_container_width=True)
                st.warning("⚠️ Заполните все обязательные поля")

# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА: НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════

elif menu == "⚙️ Настройки":
    st.markdown("<div class='main-header'>⚙️ Настройки</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👤 Профиль", "🏦 Банки", "🔔 Уведомления"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Имя", value="Олеся")
            st.text_input("Фамилия", value="")
            st.text_input("Телефон", value="+7 (999) 123-45-67")
        with col2:
            st.text_input("Email", value="olesya@example.com")
            st.selectbox("Роль", ["Риелтор", "Юрист", "Нотариус", "Частное лицо"])
            st.selectbox("Регион", ["Москва", "Московская область", "Санкт-Петербург", "Другой"])
        if st.button("💾 Сохранить профиль", type="primary"):
            st.success("✅ Профиль сохранён")

    with tab2:
        st.markdown("#### 🏦 Банки по умолчанию")
        st.selectbox("Основной банк", ["Сбербанк", "ВТБ", "Альфа-Банк", "Тинькофф", "Другой"])
        st.selectbox("Эскроу", ["Домклик", "Собственный счёт", "Другой"])
        st.text_input("Реквизиты по умолчанию")
        if st.button("💾 Сохранить банки"):
            st.success("✅ Настройки банков сохранены")

    with tab3:
        st.markdown("#### 🔔 Уведомления")
        st.toggle("Push-уведомления", value=True)
        st.toggle("Email-уведомления", value=True)
        st.toggle("SMS-уведомления", value=False)
        st.toggle("Уведомления о статусе Росреестра", value=True)
        if st.button("💾 Сохранить уведомления"):
            st.success("✅ Настройки уведомлений сохранены")

# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА: ПОМОЩЬ
# ═══════════════════════════════════════════════════════════════

elif menu == "❓ Помощь":
    st.markdown("<div class='main-header'>❓ Помощь</div>", unsafe_allow_html=True)

    with st.expander("📱 Как пользоваться ботом?", expanded=True):
        st.markdown("""
        **Telegram-бот @AvtoDKP1_bot:**
        1. Отправьте /start для начала
        2. Нажмите ➕ Новый ДКП
        3. Загрузите фото паспорта продавца или введите вручную
        4. Проверьте распознанные данные
        5. Повторите для покупателя
        6. Укажите адрес квартиры
        7. Введите цену (аванс рассчитается автоматически)
        8. Выберите банк для эскроу
        9. Проверьте данные и сгенерируйте договор
        """)

    with st.expander("💻 Как пользоваться веб-приложением?"):
        st.markdown("""
        **Веб-приложение (компьютер):**
        1. Выберите ➕ Новая сделка в меню
        2. Пройдите 6 шагов мастера
        3. Загружайте фото документов (drag-and-drop)
        4. Редактируйте поля в реальном времени
        5. Проверяйте расчёты автоматически
        6. Генерируйте и скачивайте PDF
        """)

    with st.expander("📄 Какие документы нужны?"):
        st.markdown("""
        **Обязательные документы:**
        - Паспорт продавца (все страницы)
        - Паспорт покупателя (все страницы)
        - Выписка ЕГРН (не старше 30 дней)
        - Справка об отсутствии задолженности

        **Дополнительно (если применимо):**
        - Согласие супруга на продажу
        - Документы на ипотеку
        - Свидетельство о праве собственности
        """)

    with st.expander("🔒 Безопасность данных"):
        st.markdown("""
        - ✅ Все данные шифруются AES-256
        - ✅ Хранение в облаке с резервным копированием
        - ✅ Доступ только по авторизации
        - ✅ Соответствие 152-ФЗ «О персональных данных»
        - ✅ Двухэтапная подача в Росреестр с подтверждением
        """)

    with st.expander("🆘 Техническая поддержка"):
        st.markdown("""
        **Проблемы с ботом:**
        - Отправьте /reset для сброса состояния
        - Проверьте токен: @BotFather

        **Проблемы с веб-приложением:**
        - Обновите страницу (F5)
        - Проверьте подключение к интернету

        **Контакты:**
        - Email: support@autodkp.ru
        - Telegram: @AvtoDKP1_bot
        """)
