"""تقارير الأداء — للمدير فقط."""

import pandas as pd
import streamlit as st

from models.ticket import list_tickets
from utils.sla import PRIORITY_LABELS, STATUS_LABELS, hours_between, is_breached
from utils.styles import page_header


def render(user: dict) -> None:
    page_header("تقارير الأداء", "مؤشرات تساعد على قياس جودة الدعم الفني")

    tickets = list_tickets()
    if not tickets:
        st.info("لا توجد بيانات كافية لبناء التقارير.")
        return

    closed = [t for t in tickets if t["status"] == "closed"]

    response_times = [
        h for t in tickets
        if (h := hours_between(t.get("created_at"), t.get("first_response_at"))) is not None
    ]
    resolution_times = [
        h for t in closed
        if (h := hours_between(t.get("created_at"), t.get("closed_at"))) is not None
    ]
    compliant = [t for t in closed if not is_breached(t)]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "متوسط وقت الاستجابة",
        f"{sum(response_times) / len(response_times):.1f} س" if response_times else "—",
    )
    c2.metric(
        "متوسط وقت الإغلاق",
        f"{sum(resolution_times) / len(resolution_times):.1f} س" if resolution_times else "—",
    )
    c3.metric(
        "نسبة الالتزام بالـ SLA",
        f"{len(compliant) / len(closed) * 100:.0f}%" if closed else "—",
    )
    c4.metric("نسبة الإغلاق", f"{len(closed) / len(tickets) * 100:.0f}%")

    st.divider()

    st.markdown("#### أداء الفنيين")
    per_tech: dict[str, dict] = {}
    for t in tickets:
        name = t.get("assignee_name") or "غير مُسند"
        row = per_tech.setdefault(name, {"الفني": name, "المسندة": 0, "المغلقة": 0, "المتجاوزة": 0})
        row["المسندة"] += 1
        if t["status"] == "closed":
            row["المغلقة"] += 1
            if is_breached(t):
                row["المتجاوزة"] += 1

    st.dataframe(pd.DataFrame(list(per_tech.values())), use_container_width=True, hide_index=True)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### أكثر الأعطال تكرارًا")
        cats: dict[str, int] = {}
        for t in tickets:
            cats[t["category"]] = cats.get(t["category"], 0) + 1
        st.bar_chart(dict(sorted(cats.items(), key=lambda x: -x[1])))

    with col_b:
        st.markdown("#### التوزيع حسب الأولوية")
        prios: dict[str, int] = {}
        for t in tickets:
            label = PRIORITY_LABELS.get(t["priority"], t["priority"])
            prios[label] = prios.get(label, 0) + 1
        st.bar_chart(prios)

    st.divider()
    st.markdown("#### تصدير البيانات")

    export_rows = [
        {
            "رقم التذكرة": t["id"],
            "العنوان": t["title"],
            "التصنيف": t["category"],
            "الأولوية": PRIORITY_LABELS.get(t["priority"], t["priority"]),
            "الحالة": STATUS_LABELS.get(t["status"], t["status"]),
            "مقدم الطلب": t.get("creator_name"),
            "الفني": t.get("assignee_name") or "",
            "تاريخ الفتح": t.get("created_at"),
            "تاريخ الإغلاق": t.get("closed_at") or "",
            "تجاوز SLA": "نعم" if is_breached(t) else "لا",
        }
        for t in tickets
    ]
    df = pd.DataFrame(export_rows)
    st.download_button(
        "تحميل التقرير (CSV)",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="helpdesk_report.csv",
        mime="text/csv",
        use_container_width=True,
    )
