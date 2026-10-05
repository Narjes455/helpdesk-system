"""إدارة المستخدمين — للمدير فقط."""

import pandas as pd
import streamlit as st

from models.user import create_user, email_exists, list_users, set_active
from utils.sla import ROLE_LABELS
from utils.styles import page_header


def render(user: dict) -> None:
    page_header("إدارة المستخدمين", "إضافة الموظفين والفنيين وتحديد صلاحياتهم")

    tab_list, tab_add = st.tabs(["المستخدمون", "إضافة مستخدم"])

    with tab_list:
        users = list_users()
        rows = [
            {
                "الرقم": u["id"],
                "الاسم": u["name"],
                "البريد": u["email"],
                "الدور": ROLE_LABELS.get(u["role"], u["role"]),
                "القسم": u.get("department") or "",
                "نشط": "نعم" if u.get("is_active") else "لا",
            }
            for u in users
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("##### تفعيل / تعطيل حساب")
        names = {f"{u['name']} ({u['email']})": u for u in users if u["id"] != user["id"]}
        if names:
            chosen = st.selectbox("المستخدم", list(names.keys()))
            target = names[chosen]
            col1, col2 = st.columns(2)
            if col1.button("تفعيل", use_container_width=True):
                set_active(target["id"], True)
                st.success("تم التفعيل.")
                st.rerun()
            if col2.button("تعطيل", use_container_width=True):
                set_active(target["id"], False)
                st.success("تم التعطيل.")
                st.rerun()

    with tab_add:
        with st.form("add_user", clear_on_submit=True):
            name = st.text_input("الاسم الكامل")
            email = st.text_input("البريد الإلكتروني")
            department = st.text_input("القسم")
            role_label = st.selectbox("الدور", list(ROLE_LABELS.values()))
            password = st.text_input("كلمة المرور الأولية", type="password")
            submitted = st.form_submit_button("إضافة", use_container_width=True)

        if submitted:
            if not (name.strip() and email.strip() and password):
                st.warning("الاسم والبريد وكلمة المرور مطلوبة.")
            elif email_exists(email):
                st.error("هذا البريد مسجّل مسبقًا.")
            else:
                role = next(k for k, v in ROLE_LABELS.items() if v == role_label)
                create_user(name.strip(), email, password, role, department.strip())
                st.success("تمت إضافة المستخدم.")
