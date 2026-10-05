"""لوحة المؤشرات الرئيسية."""

import streamlit as st

from models.ticket import list_tickets
from utils.sla import PRIORITY_LABELS, STATUS_LABELS, is_breached
from utils.styles import page_header


def _scoped_tickets(user: dict) -> list:
    """كل مستخدم يرى ما يخصه فقط."""
    if user["role"] == "employee":
        return list_tickets(user_id=user["id"])
    if user["role"] == "technician":
        return list_tickets(assigned_to=user["id"])
    return list_tickets()


def render(user: dict) -> None:
    page_header("لوحة المؤشرات", f"مرحبًا {user['name']}")

    tickets = _scoped_tickets(user)

    if not tickets:
        st.info("لا توجد تذاكر حتى الآن.")
        return

    open_tickets = [t for t in tickets if t["status"] != "closed"]
    closed_tickets = [t for t in tickets if t["status"] == "closed"]
    breached = [t for t in open_tickets if is_breached(t)]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي التذاكر", len(tickets))
    c2.metric("مفتوحة", len(open_tickets))
    c3.metric("مغلقة", len(closed_tickets))
    c4.metric("متجاوزة المدة", len(breached))

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### التوزيع حسب الحالة")
        counts = {}
        for t in tickets:
            label = STATUS_LABELS.get(t["status"], t["status"])
            counts[label] = counts.get(label, 0) + 1
        st.bar_chart(counts)

    with col_b:
        st.markdown("#### التوزيع حسب الأولوية")
        counts = {}
        for t in tickets:
            label = PRIORITY_LABELS.get(t["priority"], t["priority"])
            counts[label] = counts.get(label, 0) + 1
        st.bar_chart(counts)

    if breached:
        st.divider()
        st.markdown("#### 🔴 تذاكر تجاوزت المدة المحددة")
        for t in breached[:10]:
            st.write(
                f"**#{t['id']}** — {t['title']} "
                f"({PRIORITY_LABELS.get(t['priority'], t['priority'])})"
            )
