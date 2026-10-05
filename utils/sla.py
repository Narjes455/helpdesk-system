"""قواعد اتفاقية مستوى الخدمة (SLA) والمسميات العربية للحالات والأولويات."""

from datetime import datetime, timedelta

# عدد الساعات المسموح بها لإغلاق التذكرة حسب الأولوية
SLA_HOURS = {
    "critical": 2,
    "high": 4,
    "medium": 8,
    "low": 24,
}

PRIORITY_LABELS = {
    "critical": "حرجة",
    "high": "عالية",
    "medium": "متوسطة",
    "low": "منخفضة",
}

STATUS_LABELS = {
    "new": "جديدة",
    "in_review": "قيد المراجعة",
    "in_progress": "قيد المعالجة",
    "waiting_user": "بانتظار المستخدم",
    "closed": "مغلقة",
}

ROLE_LABELS = {
    "employee": "موظف",
    "technician": "فني دعم",
    "manager": "مدير",
}

CATEGORIES = [
    "شبكة وإنترنت",
    "أجهزة وطابعات",
    "برامج وأنظمة",
    "حسابات وصلاحيات",
    "بريد إلكتروني",
    "أخرى",
]

OPEN_STATUSES = ("new", "in_review", "in_progress", "waiting_user")


def parse_dt(value) -> datetime | None:
    """تحويل القيمة القادمة من قاعدة البيانات إلى datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def calculate_due_date(priority: str, start: datetime | None = None) -> datetime:
    """حساب الموعد النهائي للتذكرة بناءً على أولويتها."""
    start = start or datetime.now()
    return start + timedelta(hours=SLA_HOURS.get(priority, 8))


def is_breached(ticket: dict) -> bool:
    """هل تجاوزت التذكرة مدة الـ SLA؟"""
    due = parse_dt(ticket.get("due_at"))
    if due is None:
        return False
    reference = parse_dt(ticket.get("closed_at")) or datetime.now()
    return reference > due


def hours_between(start, end) -> float | None:
    """عدد الساعات بين تاريخين (مقرّبة لخانتين)."""
    a, b = parse_dt(start), parse_dt(end)
    if a is None or b is None:
        return None
    return round((b - a).total_seconds() / 3600, 2)


def sla_badge(ticket: dict) -> str:
    """نص قصير يوضح حالة الالتزام بالـ SLA."""
    if ticket.get("status") == "closed":
        return "❌ تجاوز" if is_breached(ticket) else "✅ ملتزم"
    return "🔴 متأخرة" if is_breached(ticket) else "🟢 ضمن المدة"
