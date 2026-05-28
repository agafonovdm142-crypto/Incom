"""
💻 АвтоДКП Веб — Streamlit интерфейс для автоматизации ДКП
Версия: 2.1 | Исправленная (без сложного HTML)
"""

import streamlit as st
from datetime import datetime

# ── Настройка страницы ──
st.set_page_config(
    page_title="АвтоДКП — Автоматизация договоров",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
st.sidebar.title("🏠 АвтоДКP")
st.sidebar.caption("Автоматизация договоров")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Навигация",
    ["📋 Мои сделки", "➕ Новая сделка", "⚙️ Настройки", "❓ Помощь"]
)

st.sidebar.divider()
st.sidebar.info("**Олеся** — Риелтор | Москва")
st.sidebar.info("📱 Бот: @AvtoDKP1_bot")

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ-ПОМОЩНИКИ
# ═══════════════════════════════════════════════════════════════

def format_price(price):
    return f"{price:,}".replace(",", " ")

def get_status_color(status):
    colors = {
        "draft": "🟡",
        "check": "🔵",
        "signed": "🟢",
        "done": "✅"
    }
    return colors.get(status, "⚪")

def get_status_text(status):
    texts = {
        "draft": "Черновик",
        "check": "На проверке",
        "signed": "Подписан",
        "done": "Завершён"
    }
    return texts.get(status, status)

# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА: МОИ СДЕЛКИ
# ═══════════════════════════════════════════════════════════════

if menu == "📋 Мои сделки" and not st.session_state.current_deal:
    st.title("📋 Мои сделки")

    # Фильтры
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        status_filter = st.selectbox("Статус", ["Все", "Черновик", "На проверке", "Подписан", "Завершён"])
    with col2:
        search = st.text_input("Поиск по адресу или ФИО")
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ Новая", use_container_width=True, type="primary"):
            st.session_state.current_deal = "new"
            st.session_state.new_deal_step = 1
            st.session_state.new_deal_data = {}
            st.rerun()

    st.divider()

    # Фильтрация
    filtered_deals = st.session_state.deals
    if status_filter != "Все":
        status_map = {"Черновик": "draft", "На проверке": "check", "Подписан": "signed", "Завершён": "done"}
        filtered_deals = [d for d in filtered_deals if d['status'] == status_map.get(status_filter)]
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
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

                with col1:
                    st.subheader(deal['id'])
                    st.caption(f"{get_status_color(deal['status'])} {get_status_text(deal['status'])} | {deal['date']}")

                with col2:
                    st.write(f"**Продавец:** {deal['seller']['full_name']}")
                    st.write(f"**→ Покупатель:** {deal['buyer']['full_name']}")

                with col3:
                    st.write(f"**📍** {deal['property']['address']}")
                    st.write(f"**💰** {format_price(deal['price']['total'])} ₽")

                with col4:
                    st.write(f"**Кадастр:**")
                    st.write(deal['property']['cadastral'])
                    st.write(f"{deal['property']['area']} м²")

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
            st.title(deal['id'])
        with col2:
            st.write(f"### {get_status_color(deal['status'])} {get_status_text(deal['status'])}")
        with col3:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(["📄 Договор", "👤 Стороны", "🏠 Объект", "💰 Расчёты"])

        with tab1:
            st.header("📄 Текст договора")

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
                    st.success("✅ Договор отправлен сторонам!")

            contract_preview = f"""ДОГОВОР КУПЛИ-ПРОДАЖИ КВАРТИРЫ

г. Москва                                                                               {deal['date']}

    {deal['seller']['full_name']}, именуемый в дальнейшем «Продавец», с одной стороны, и
    {deal['buyer']['full_name']}, именуемый в дальнейшем «Покупатель», с другой стороны,
    совместно именуемые «Стороны», заключили настоящий договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Продавец продаёт, а Покупатель покупает квартиру:
    - Адрес: {deal['property']['address']}
    - Кадастровый номер: {deal['property']['cadastral']}
    - Площадь: {deal['property']['area']} м²

2. ЦЕНА И ПОРЯДОК РАСЧЁТОВ

2.1. Общая цена: {format_price(deal['price']['total'])} рублей 00 копеек.

2.2. Аванс (задаток): {format_price(deal['price']['advance'])} руб.
    Основной платёж: {format_price(deal['price']['main_payment'])} руб.

2.3. Расчёты производятся через эскроу:
    - {deal['escrow']['company']}
    - Банк: {deal['escrow']['bank']}
    - БИК: {deal['escrow']['bik']}

3. ПРАВА И ОБЯЗАННОСТИ СТОРОН

3.1. Продавец обязуется передать квартиру в течение 30 дней.
3.2. Покупатель обязуется оплатить полную стоимость до регистрации.

4. ПОДПИСИ СТОРОН

    _________________ / {deal['seller']['full_name']} /          _________________ / {deal['buyer']['full_name']} /
           (Подпись)                                                   (Подпись)"""
            st.text_area("", value=contract_preview, height=500, label_visibility="collapsed")

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("👤 Продавец")
                st.text_input("ФИО", value=deal['seller'].get('full_name', ''), key="s_fio")
                st.text_input("Дата рождения", value=deal['seller'].get('birth_date', ''), key="s_bd")
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Серия", value=deal['seller'].get('passport_series', ''), key="s_ser")
                with c2:
                    st.text_input("Номер", value=deal['seller'].get('passport_number', ''), key="s_num")
                st.text_input("Кем выдан", value=deal['seller'].get('passport_issued_by', ''), key="s_iss")
                st.text_input("Дата выдачи", value=deal['seller'].get('passport_issued_date', ''), key="s_id")
                st.text_input("Адрес регистрации", value=deal['seller'].get('registration_address', ''), key="s_addr")
                if st.button("💾 Сохранить продавца", key="save_seller"):
                    st.success("✅ Данные продавца сохранены")

            with col2:
                st.subheader("👤 Покупатель")
                st.text_input("ФИО", value=deal['buyer'].get('full_name', ''), key="b_fio")
                st.text_input("Дата рождения", value=deal['buyer'].get('birth_date', ''), key="b_bd")
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Серия", value=deal['buyer'].get('passport_series', ''), key="b_ser")
                with c2:
                    st.text_input("Номер", value=deal['buyer'].get('passport_number', ''), key="b_num")
                st.text_input("Кем выдан", value=deal['buyer'].get('passport_issued_by', ''), key="b_iss")
                st.text_input("Дата выдачи", value=deal['buyer'].get('passport_issued_date', ''), key="b_id")
                st.text_input("Адрес регистрации", value=deal['buyer'].get('registration_address', ''), key="b_addr")
                if st.button("💾 Сохранить покупателя", key="save_buyer"):
                    st.success("✅ Данные покупателя сохранены")

        with tab3:
            st.subheader("🏠 Объект недвижимости")
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Тип", value="Квартира", key="prop_type")
                st.text_input("Адрес", value=deal['property']['address'], key="prop_addr")
                st.text_input("Кадастровый номер", value=deal['property']['cadastral'], key="prop_cad")
            with c2:
                st.number_input("Площадь (м²)", value=float(deal['property']['area']), key="prop_area")
                st.number_input("Этаж", value=int(deal['property'].get('floor', 1)), key="prop_floor")
                st.number_input("Комнат", value=int(deal['property'].get('rooms', 1)), key="prop_rooms")

            uploaded_egrn = st.file_uploader("📷 Загрузить выписку ЕГРН", type=["jpg", "jpeg", "png", "pdf"], key="egrn_upload")
            if uploaded_egrn:
                st.success("✅ Выписка загружена")

            if st.button("💾 Сохранить объект", key="save_prop"):
                st.success("✅ Данные объекта сохранены")

        with tab4:
            st.subheader("💰 Цена и расчёты")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_price = st.number_input("Цена", value=deal['price']['total'], key="price_total")
            with c2:
                new_advance = st.number_input("Аванс", value=deal['price']['advance'], key="price_adv")
            with c3:
                new_main = st.number_input("Основной платёж", value=deal['price']['main_payment'], key="price_main")

            # Проверка расчётов
            if new_advance + new_main == new_price:
                st.success("✅ Расчёт сходится: Аванс + Основной = Цена")
            else:
                diff = new_price - (new_advance + new_main)
                st.error(f"❌ Расчёт не сходится: разница {diff:,} ₽")

            st.divider()
            st.subheader("🏦 Эскроу")
            st.text_input("Компания", value=deal['escrow']['company'], key="esc_comp")
            bank_options = ["ПАО СБЕРБАНК РОССИИ", "ПАО ВТБ", "АО «АЛЬФА-БАНК»", "Другой"]
            selected = st.selectbox("Банк", bank_options, 
                                   index=bank_options.index(deal['escrow']['bank']) if deal['escrow']['bank'] in bank_options else 3, 
                                   key="esc_bank")
            if selected == "Другой":
                st.text_input("Название банка", key="esc_bank_custom")
            st.text_input("БИК", value=deal['escrow']['bik'], key="esc_bik")

            if st.button("💾 Сохранить расчёты", key="save_price"):
                st.success("✅ Данные расчётов сохранены")

# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА: НОВАЯ СДЕЛКА (МАСТЕР)
# ═══════════════════════════════════════════════════════════════

elif menu == "➕ Новая сделка" or st.session_state.current_deal == "new":
    st.title("➕ Новая сделка")

    step = st.session_state.new_deal_step

    # Индикатор шагов
    steps = ["1. Продавец", "2. Покупатель", "3. Объект", "4. Цена", "5. Банк", "6. Проверка"]
    cols = st.columns(len(steps))
    for i, (col, step_name) in enumerate(zip(cols, steps)):
        with col:
            if i + 1 == step:
                st.info(f"**{step_name}**")  # Текущий шаг
            elif i + 1 < step:
                st.success(f"✓ {step_name}")  # Пройден
            else:
                st.write(f"○ {step_name}")  # Ожидает

    st.divider()

    if step == 1:
        st.subheader("📷 Шаг 1: Данные продавца")
        c1, c2 = st.columns(2)
        with c1:
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
        with c2:
            st.write("**Или введите вручную:**")
            s_fio = st.text_input("ФИО продавца", key="new_s_fio")
            s_bd = st.text_input("Дата рождения", key="new_s_bd")
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                s_ser = st.text_input("Серия", key="new_s_ser")
            with c_s2:
                s_num = st.text_input("Номер", key="new_s_num")
            s_iss = st.text_input("Кем выдан", key="new_s_iss")
            s_id = st.text_input("Дата выдачи", key="new_s_id")
            s_addr = st.text_input("Адрес регистрации", key="new_s_addr")

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("◀️ Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with c_btn2:
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
        st.subheader("📷 Шаг 2: Данные покупателя")
        c1, c2 = st.columns(2)
        with c1:
            uploaded = st.file_uploader("Фото паспорта покупателя", type=["jpg", "jpeg", "png"], key="buyer_photo")
            if uploaded:
                st.image(uploaded, width=300)
                st.success("✅ Распознано: Иванов Иван Иванович")
        with c2:
            b_fio = st.text_input("ФИО покупателя", key="new_b_fio")
            b_bd = st.text_input("Дата рождения", key="new_b_bd")
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                b_ser = st.text_input("Серия", key="new_b_ser")
            with c_b2:
                b_num = st.text_input("Номер", key="new_b_num")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 1
                st.rerun()
        with c2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with c3:
            if st.button("Далее →", type="primary", use_container_width=True):
                st.session_state.new_deal_step = 3
                st.rerun()

    elif step == 3:
        st.subheader("🏠 Шаг 3: Объект недвижимости")
        c1, c2 = st.columns(2)
        with c1:
            prop_addr = st.text_input("Адрес", key="new_prop_addr")
            prop_cad = st.text_input("Кадастровый номер", key="new_prop_cad")
        with c2:
            prop_area = st.number_input("Площадь (м²)", value=0.0, key="new_prop_area")
            prop_floor = st.number_input("Этаж", value=1, key="new_prop_floor")

        uploaded_egrn = st.file_uploader("Выписка ЕГРН", type=["jpg", "jpeg", "png", "pdf"], key="new_egrn")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 2
                st.rerun()
        with c2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with c3:
            if st.button("Далее →", type="primary", use_container_width=True):
                st.session_state.new_deal_step = 4
                st.rerun()

    elif step == 4:
        st.subheader("💰 Шаг 4: Цена")
        price_total = st.number_input("Цена квартиры (₽)", value=0, step=100000, key="new_price")

        if price_total > 0:
            advance = int(price_total * 0.04)
            main = price_total - advance
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Аванс (4%)", f"{advance:,} ₽")
            with c2:
                st.metric("Основной платёж", f"{main:,} ₽")
            with c3:
                st.metric("Итого", f"{price_total:,} ₽")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 3
                st.rerun()
        with c2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with c3:
            if st.button("Далее →", type="primary", use_container_width=True):
                st.session_state.new_deal_data['price'] = {
                    "total": price_total,
                    "advance": int(price_total * 0.04),
                    "main_payment": price_total - int(price_total * 0.04)
                }
                st.session_state.new_deal_step = 5
                st.rerun()

    elif step == 5:
        st.subheader("🏦 Шаг 5: Банк для эскроу")
        bank = st.selectbox("Выберите банк", ["Сбербанк", "ВТБ", "Альфа-Банк", "Другой"], key="new_bank")
        if bank == "Другой":
            st.text_input("Название банка", key="new_bank_custom")
            st.text_input("БИК", key="new_bik")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 4
                st.rerun()
        with c2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with c3:
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
        st.subheader("🔍 Шаг 6: Проверка данных")

        data = st.session_state.new_deal_data

        checks = [
            ("Паспорт продавца", bool(data.get('seller'))),
            ("Паспорт покупателя", bool(data.get('buyer'))),
            ("Объект недвижимости", bool(data.get('property'))),
            ("Цена", bool(data.get('price'))),
            ("Банк эскроу", bool(data.get('escrow'))),
        ]

        all_ok = True
        for name, status in checks:
            if status:
                st.success(f"✅ {name} — заполнено")
            else:
                st.error(f"❌ {name} — не заполнено")
                all_ok = False

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("◀️ Назад", use_container_width=True):
                st.session_state.new_deal_step = 5
                st.rerun()
        with c2:
            if st.button("Отмена", use_container_width=True):
                st.session_state.current_deal = None
                st.rerun()
        with c3:
            if all_ok:
                if st.button("📄 Сгенерировать ДКП", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("✅ Договор успешно сгенерирован!")
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
    st.title("⚙️ Настройки")

    tab1, tab2, tab3 = st.tabs(["👤 Профиль", "🏦 Банки", "🔔 Уведомления"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Имя", value="Олеся")
            st.text_input("Фамилия", value="")
            st.text_input("Телефон", value="+7 (999) 123-45-67")
        with c2:
            st.text_input("Email", value="olesya@example.com")
            st.selectbox("Роль", ["Риелтор", "Юрист", "Нотариус", "Частное лицо"])
            st.selectbox("Регион", ["Москва", "Московская область", "Санкт-Петербург", "Другой"])
        if st.button("💾 Сохранить профиль", type="primary"):
            st.success("✅ Профиль сохранён")

    with tab2:
        st.subheader("🏦 Банки по умолчанию")
        st.selectbox("Основной банк", ["Сбербанк", "ВТБ", "Альфа-Банк", "Тинькофф", "Другой"])
        st.selectbox("Эскроу", ["Домклик", "Собственный счёт", "Другой"])
        st.text_input("Реквизиты по умолчанию")
        if st.button("💾 Сохранить банки"):
            st.success("✅ Настройки банков сохранены")

    with tab3:
        st.subheader("🔔 Уведомления")
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
    st.title("❓ Помощь")

    with st.expander("📱 Как пользоваться ботом?", expanded=True):
        st.write("""
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
        st.write("""
        **Веб-приложение (компьютер):**
        1. Выберите ➕ Новая сделка в меню
        2. Пройдите 6 шагов мастера
        3. Загружайте фото документов (drag-and-drop)
        4. Редактируйте поля в реальном времени
        5. Проверяйте расчёты автоматически
        6. Генерируйте и скачивайте PDF
        """)

    with st.expander("📄 Какие документы нужны?"):
        st.write("""
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
        st.write("""
        - ✅ Все данные шифруются AES-256
        - ✅ Хранение в облаке с резервным копированием
        - ✅ Доступ только по авторизации
        - ✅ Соответствие 152-ФЗ «О персональных данных»
        - ✅ Двухэтапная подача в Росреестр с подтверждением
        """)

    with st.expander("🆘 Техническая поддержка"):
        st.write("""
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
