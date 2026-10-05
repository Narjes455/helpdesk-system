"""صفحة تسجيل الدخول."""

import streamlit as st

from models.user import authenticate


def render() -> None:
    st.markdown("## 🎫 نظام تذاكر الدعم الفني")
    st.caption("سجّل دخولك للمتابعة")

    col_form, _ = st.columns([2, 1])

    with col_form:
        with st.form("login_form"):
            email = st.text_input("البريد الإلكتروني")
            password = st.text_input("كلمة المرور", type="password")
            submitted = st.form_submit_button("تسجيل الدخول", use_container_width=True)

        if submitted:
            if not email or not password:
                st.warning("الرجاء تعبئة جميع الحقول.")
                return

            user = authenticate(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة.")

        with st.expander("حسابات تجريبية (بعد تشغيل seed.py)"):
            st.write("**مدير:** manager@example.com / 123456")
            st.write("**فني دعم:** tech1@example.com / 123456")
            st.write("**موظف:** employee1@example.com / 123456")
