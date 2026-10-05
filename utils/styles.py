"""تنسيقات الواجهة ودعم اتجاه النص من اليمين لليسار."""

import streamlit as st

RTL_CSS = """
<style>
    .stApp, .stApp * {
        direction: rtl;
        text-align: right;
        font-family: "Segoe UI", "Tahoma", sans-serif;
    }
    section[data-testid="stSidebar"] { direction: rtl; }
    .stApp [data-testid="stMetricValue"] { direction: ltr; text-align: center; }
    .stDataFrame { direction: ltr; }
    .ticket-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        background: #ffffff;
    }
    .ticket-card h4 { margin: 0 0 6px 0; }
    .meta { color: #666; font-size: 0.85rem; }
</style>
"""


def apply_rtl() -> None:
    """تطبيق تنسيق RTL على الصفحة."""
    st.markdown(RTL_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    """عنوان موحّد لكل صفحة."""
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
    st.divider()
