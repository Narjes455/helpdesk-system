"""عمليات التذاكر."""

from datetime import datetime

from database.connection import execute, query_all, query_one
from models.action_log import add_log
from utils.sla import OPEN_STATUSES, calculate_due_date

BASE_SELECT = """
    SELECT t.*,
           creator.name  AS creator_name,
           assignee.name AS assignee_name
    FROM tickets t
    JOIN users creator  ON creator.id = t.created_by
    LEFT JOIN users assignee ON assignee.id = t.assigned_to
"""


def create_ticket(
    title: str,
    description: str,
    category: str,
    priority: str,
    created_by: int,
) -> int:
    """فتح تذكرة جديدة مع حساب الموعد النهائي تلقائيًا."""
    now = datetime.now()
    due = calculate_due_date(priority, now)

    ticket_id = execute(
        """INSERT INTO tickets (title, description, category, priority, status,
                                created_by, created_at, due_at)
           VALUES (?, ?, ?, ?, 'new', ?, ?, ?)""",
        (
            title,
            description,
            category,
            priority,
            created_by,
            now.isoformat(timespec="seconds"),
            due.isoformat(timespec="seconds"),
        ),
    )
    add_log(ticket_id, created_by, "فتح التذكرة", f"الأولوية: {priority}")
    return ticket_id


def get_ticket(ticket_id: int) -> dict | None:
    return query_one(BASE_SELECT + " WHERE t.id = ?", (ticket_id,))


def list_tickets(
    user_id: int | None = None,
    assigned_to: int | None = None,
    status: str | None = None,
    only_open: bool = False,
) -> list:
    """جلب التذاكر مع مرشحات اختيارية."""
    clauses, params = [], []

    if user_id is not None:
        clauses.append("t.created_by = ?")
        params.append(user_id)
    if assigned_to is not None:
        clauses.append("t.assigned_to = ?")
        params.append(assigned_to)
    if status:
        clauses.append("t.status = ?")
        params.append(status)
    if only_open:
        placeholders = ", ".join("?" for _ in OPEN_STATUSES)
        clauses.append(f"t.status IN ({placeholders})")
        params.extend(OPEN_STATUSES)

    sql = BASE_SELECT
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY t.created_at DESC"

    return query_all(sql, tuple(params))


def update_status(ticket_id: int, new_status: str, user_id: int, note: str = "") -> None:
    """تغيير حالة التذكرة مع تسجيل وقت أول استجابة ووقت الإغلاق."""
    ticket = get_ticket(ticket_id)
    if not ticket:
        return

    now = datetime.now().isoformat(timespec="seconds")

    if ticket.get("first_response_at") is None and new_status != "new":
        execute("UPDATE tickets SET first_response_at = ? WHERE id = ?", (now, ticket_id))

    if new_status == "closed":
        execute(
            "UPDATE tickets SET status = ?, closed_at = ? WHERE id = ?",
            (new_status, now, ticket_id),
        )
    else:
        execute(
            "UPDATE tickets SET status = ?, closed_at = NULL WHERE id = ?",
            (new_status, ticket_id),
        )

    add_log(ticket_id, user_id, f"تغيير الحالة إلى: {new_status}", note)


def assign_ticket(ticket_id: int, technician_id: int, user_id: int) -> None:
    """إسناد التذكرة إلى فني."""
    execute("UPDATE tickets SET assigned_to = ? WHERE id = ?", (technician_id, ticket_id))
    add_log(ticket_id, user_id, "إسناد التذكرة", f"إلى الفني رقم {technician_id}")


def update_priority(ticket_id: int, priority: str, user_id: int) -> None:
    """تعديل الأولوية وإعادة حساب الموعد النهائي."""
    ticket = get_ticket(ticket_id)
    if not ticket:
        return
    created = ticket.get("created_at")
    start = datetime.fromisoformat(str(created)) if created else datetime.now()
    due = calculate_due_date(priority, start)
    execute(
        "UPDATE tickets SET priority = ?, due_at = ? WHERE id = ?",
        (priority, due.isoformat(timespec="seconds"), ticket_id),
    )
    add_log(ticket_id, user_id, "تعديل الأولوية", f"إلى: {priority}")
