"""تعبئة قاعدة البيانات ببيانات تجريبية.

التشغيل من جذر المشروع:  python -m database.seed
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import execute, init_database, query_one  # noqa: E402
from models.action_log import add_log  # noqa: E402
from models.user import create_user  # noqa: E402
from utils.sla import SLA_HOURS, calculate_due_date  # noqa: E402

DEMO_USERS = [
    ("مدير النظام", "manager@example.com", "manager", "تقنية المعلومات"),
    ("فني الدعم الأول", "tech1@example.com", "technician", "تقنية المعلومات"),
    ("فني الدعم الثاني", "tech2@example.com", "technician", "تقنية المعلومات"),
    ("موظف تجريبي 1", "employee1@example.com", "employee", "المحاسبة"),
    ("موظف تجريبي 2", "employee2@example.com", "employee", "الموارد البشرية"),
]

DEMO_TICKETS = [
    ("الطابعة لا تستجيب", "طابعة قسم المحاسبة لا تطبع رغم اتصالها بالشبكة.", "أجهزة وطابعات", "high"),
    ("انقطاع الإنترنت بالدور الثاني", "الشبكة متقطعة منذ الصباح في مكاتب الدور الثاني.", "شبكة وإنترنت", "critical"),
    ("نسيان كلمة مرور النظام", "لا أستطيع الدخول إلى النظام الداخلي.", "حسابات وصلاحيات", "medium"),
    ("بطء في فتح ملفات Excel", "الملفات الكبيرة تستغرق وقتًا طويلًا للفتح.", "برامج وأنظمة", "low"),
    ("عدم وصول رسائل البريد", "الرسائل الواردة من الموردين لا تصل منذ يومين.", "بريد إلكتروني", "high"),
    ("شاشة الجهاز لا تعمل", "جهاز مكتب مدخل البيانات لا يظهر أي صورة.", "أجهزة وطابعات", "high"),
    ("طلب تركيب برنامج AutoCAD", "مطلوب تركيب البرنامج على جهاز المهندس.", "برامج وأنظمة", "medium"),
    ("صلاحيات مجلد المشاريع", "أحتاج صلاحية قراءة لمجلد المشاريع المشترك.", "حسابات وصلاحيات", "low"),
]


def seed() -> None:
    init_database()

    if query_one("SELECT id FROM users LIMIT 1"):
        print("⚠️  قاعدة البيانات تحتوي على بيانات مسبقًا. احذف helpdesk.db وأعد المحاولة.")
        return

    user_ids = {}
    for name, email, role, dept in DEMO_USERS:
        user_ids[email] = create_user(name, email, "123456", role, dept)
    print(f"✅ تم إنشاء {len(user_ids)} مستخدمين (كلمة المرور: 123456)")

    technicians = [user_ids["tech1@example.com"], user_ids["tech2@example.com"]]
    employees = [user_ids["employee1@example.com"], user_ids["employee2@example.com"]]

    statuses = ["new", "in_review", "in_progress", "waiting_user", "closed", "closed", "closed"]

    for index, (title, desc, category, priority) in enumerate(DEMO_TICKETS):
        creator = random.choice(employees)
        created = datetime.now() - timedelta(days=random.randint(0, 20), hours=random.randint(0, 20))
        due = calculate_due_date(priority, created)
        status = statuses[index % len(statuses)]
        assignee = random.choice(technicians) if status != "new" else None

        sla_hours = SLA_HOURS[priority]
        first_response = (
            created + timedelta(hours=random.uniform(0.2, sla_hours * 0.4))
            if status != "new"
            else None
        )
        # أغلب التذاكر تُغلق ضمن المدة، وبعضها يتجاوزها — ليظهر التقرير بشكل واقعي
        factor = random.choice([0.4, 0.6, 0.8, 0.9, 1.3])
        closed_at = created + timedelta(hours=sla_hours * factor) if status == "closed" else None

        ticket_id = execute(
            """INSERT INTO tickets (title, description, category, priority, status,
                                    created_by, assigned_to, created_at,
                                    first_response_at, closed_at, due_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                title, desc, category, priority, status, creator, assignee,
                created.isoformat(timespec="seconds"),
                first_response.isoformat(timespec="seconds") if first_response else None,
                closed_at.isoformat(timespec="seconds") if closed_at else None,
                due.isoformat(timespec="seconds"),
            ),
        )

        add_log(ticket_id, creator, "فتح التذكرة", f"التصنيف: {category}")
        if assignee:
            add_log(ticket_id, assignee, "استلام التذكرة", "تم البدء في المعالجة")
        if status == "closed":
            add_log(ticket_id, assignee or creator, "إغلاق التذكرة", "تم حل المشكلة")

    print(f"✅ تم إنشاء {len(DEMO_TICKETS)} تذاكر تجريبية")
    print("\n🚀 شغّل التطبيق الآن:  streamlit run app.py")
    print("   دخول المدير: manager@example.com / 123456")


if __name__ == "__main__":
    random.seed(7)
    seed()
