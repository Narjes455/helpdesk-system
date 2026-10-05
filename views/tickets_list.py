"""قائمة التذاكر وتفاصيل كل تذكرة."""

import streamlit as st

from models.action_log import add_log, get_logs
from models.ticket import assign_ticket, get_ticket, list_tickets, update_priority, update_status
from models.user import list_users
from utils.sla import PRIORITY_LABELS, STATUS_LABELS, sla_badge
from utils.styles import page_header


def _visible_tickets(user: dict) -> list:
    if user["role"] == "employee":
        return list_tickets(user_id=user["id"])
    return list_tickets()


def render(user: dict) -> None:
    page_header("التذاكر", "اختر تذكرة لعرض تفاصيلها واتخاذ إجراء")

    tickets = _visible_tickets(user)
    if not tickets:
        st.info("لا توجد تذاكر.")
        return

    col1, col2 = st.columns(2)
    status_filter = col1.selectbox("تصفية بالحالة", ["الكل"] + list(STATUS_LABELS.values()))
    priority_filter = col2.selectbox("تصفية بالأولوية", ["الكل"] + list(PRIORITY_LABELS.values()))

    if status_filter != "الكل":
        key = next(k for k, v in STATUS_LABELS.items() if v == status_filter)
        tickets = [t for t in tickets if t["status"] == key]
    if priority_filter != "الكل":
        key = next(k for k, v in PRIORITY_LABELS.items() if v == priority_filter)
        tickets = [t for t in tickets if t["priority"] == key]

    if not tickets:
        st.info("لا توجد تذاكر مطابقة للتصفية.")
        return

    st.caption(f"عدد النتائج: {len(tickets)}")

    options = {
        f"#{t['id']} — {t['title']} ({STATUS_LABELS.get(t['status'], t['status'])})": t["id"]
        for t in tickets
    }
    selected_label = st.selectbox("التذكرة", list(options.keys()))
    ticket_id = options[selected_label]

    st.divider()
    _render_detail(ticket_id, user)


def _render_detail(ticket_id: int, user: dict) -> None:
    ticket = get_ticket(ticket_id)
    if not ticket:
        st.error("التذكرة غير موجودة.")
        return

    st.markdown(f"### #{ticket['id']} — {ticket['title']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("الحالة", STATUS_LABELS.get(ticket["status"], ticket["status"]))
    c2.metric("الأولوية", PRIORITY_LABELS.get(ticket["priority"], ticket["priority"]))
    c3.metric("التصنيف", ticket["category"])
    c4.metric("الالتزام", sla_badge(ticket))

    st.write(f"**مقدم الطلب:** {ticket.get('creator_name', '—')}")
    st.write(f"**الفني المسؤول:** {ticket.get('assignee_name') or 'لم يُسند بعد'}")
    st.write(f"**تاريخ الفتح:** {ticket.get('created_at')}")
    st.write(f"**الموعد النهائي:** {ticket.get('due_at')}")

    with st.expander("الوصف التفصيلي", expanded=True):
        st.write(ticket["description"])

    if user["role"] in ("technician", "manager"):
        _render_actions(ticket, user)

    st.divider()
    st.markdown("#### سجل الإجراءات")
    logs = get_logs(ticket_id)
    if not logs:
        st.caption("لا توجد إجراءات مسجلة.")
    for log in logs:
        note = f" — {log['note']}" if log.get("note") else ""
        st.write(f"🕐 `{log['created_at']}` **{log['user_name']}**: {log['action']}{note}")


def _render_actions(ticket: dict, user: dict) -> None:
    st.divider()
    st.markdown("#### الإجراءات")

    col1, col2 = st.columns(2)

    with col1:
        current = STATUS_LABELS.get(ticket["status"], "جديدة")
        labels = list(STATUS_LABELS.values())
        new_label = st.selectbox("تغيير الحالة", labels, index=labels.index(current))
        note = st.text_input("ملاحظة على الإجراء", key=f"note_{ticket['id']}")

        if st.button("حفظ الحالة", use_container_width=True):
            new_status = next(k for k, v in STATUS_LABELS.items() if v == new_label)
            update_status(ticket["id"], new_status, user["id"], note)
            st.success("تم تحديث الحالة.")
            st.rerun()

    with col2:
        technicians = list_users(role="technician")
        if technicians:
            names = {t["name"]: t["id"] for t in technicians}
            chosen = st.selectbox("إسناد إلى فني", list(names.keys()))
            if st.button("إسناد", use_container_width=True):
                assign_ticket(ticket["id"], names[chosen], user["id"])
                st.success("تم الإسناد.")
                st.rerun()

        if user["role"] == "manager":
            p_labels = list(PRIORITY_LABELS.values())
            current_p = PRIORITY_LABELS.get(ticket["priority"], "متوسطة")
            new_p = st.selectbox(
                "تعديل الأولوية", p_labels, index=p_labels.index(current_p),
                key=f"prio_{ticket['id']}",
            )
            if st.button("حفظ الأولوية", use_container_width=True):
                key = next(k for k, v in PRIORITY_LABELS.items() if v == new_p)
                update_priority(ticket["id"], key, user["id"])
                st.success("تم تعديل الأولوية وإعادة حساب الموعد النهائي.")
                st.rerun()

    comment = st.text_area("إضافة ملاحظة بدون تغيير الحالة", key=f"c_{ticket['id']}")
    if st.button("إضافة الملاحظة"):
        if comment.strip():
            add_log(ticket["id"], user["id"], "ملاحظة", comment.strip())
            st.success("تمت الإضافة.")
            st.rerun()
