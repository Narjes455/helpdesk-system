"""نظام تذاكر الدعم الفني — نقطة تشغيل التطبيق.

التشغيل:  streamlit run app.py
"""

import streamlit as st

from database.connection import database_label, init_database
from utils.sla import ROLE_LABELS
from utils.styles import apply_rtl
from views import admin, dashboard, login, reports, ticket_form, tickets_list

st.set_page_config(page_title="نظام تذاكر الدعم الفني", page_icon="🎫", layout="wide")


@st.cache_resource
def _setup() -> bool:
    """تهيئة قاعدة البيانات مرة واحدة عند بدء التطبيق."""
    init_database()
    return True


# الصفحات المتاحة لكل دور
PAGES = {
    "employee": ["لوحة المؤشرات", "فتح تذكرة", "تذاكري"],
    "technician": ["لوحة المؤشرات", "التذاكر", "فتح تذكرة"],
    "manager": ["لوحة المؤشرات", "التذاكر", "فتح تذكرة", "التقارير", "إدارة المستخدمين"],
}


def main() -> None:
    _setup()
    apply_rtl()

    if "user" not in st.session_state:
        login.render()
        return

    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.caption(ROLE_LABELS.get(user["role"], user["role"]))
        st.divider()

        page = st.radio("التنقل", PAGES[user["role"]], label_visibility="collapsed")

        st.divider()
        st.caption(f"قاعدة البيانات: {database_label()}")
        if st.button("تسجيل الخروج", use_container_width=True):
            del st.session_state.user
            st.rerun()

    if page == "لوحة المؤشرات":
        dashboard.render(user)
    elif page == "فتح تذكرة":
        ticket_form.render(user)
    elif page in ("التذاكر", "تذاكري"):
        tickets_list.render(user)
    elif page == "التقارير":
        reports.render(user)
    elif page == "إدارة المستخدمين":
        admin.render(user)


if __name__ == "__main__":
    main()
