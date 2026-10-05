"""صفحة فتح تذكرة جديدة."""

import streamlit as st

from models.ticket import create_ticket
from utils.sla import CATEGORIES, PRIORITY_LABELS, SLA_HOURS
from utils.styles import page_header


def render(user: dict) -> None:
    page_header("فتح تذكرة جديدة", "صف المشكلة بدقة ليسهل حلها بسرعة")

    with st.form("new_ticket", clear_on_submit=True):
        title = st.text_input("عنوان المشكلة", max_chars=120)
        description = st.text_area("وصف تفصيلي", height=150)

        col1, col2 = st.columns(2)
        category = col1.selectbox("التصنيف", CATEGORIES)
        priority_label = col2.selectbox("الأولوية", list(PRIORITY_LABELS.values()), index=2)

        priority = next(k for k, v in PRIORITY_LABELS.items() if v == priority_label)
        st.caption(f"المدة المتوقعة للحل: {SLA_HOURS[priority]} ساعة")

        submitted = st.form_submit_button("إرسال التذكرة", use_container_width=True)

    if submitted:
        if not title.strip() or not description.strip():
            st.warning("العنوان والوصف مطلوبان.")
            return

        ticket_id = create_ticket(title.strip(), description.strip(), category, priority, user["id"])
        st.success(f"تم فتح التذكرة رقم #{ticket_id} بنجاح.")
