"""سجل الإجراءات — كل حركة على التذكرة تُسجَّل هنا."""

from datetime import datetime

from database.connection import execute, query_all


def add_log(ticket_id: int, user_id: int, action: str, note: str = "") -> int:
    """تسجيل إجراء جديد على التذكرة."""
    return execute(
        """INSERT INTO action_logs (ticket_id, user_id, action, note, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (ticket_id, user_id, action, note, datetime.now().isoformat(timespec="seconds")),
    )


def get_logs(ticket_id: int) -> list:
    """كل إجراءات تذكرة معينة مرتبة زمنيًا."""
    return query_all(
        """SELECT l.*, u.name AS user_name
           FROM action_logs l
           JOIN users u ON u.id = l.user_id
           WHERE l.ticket_id = ?
           ORDER BY l.created_at ASC""",
        (ticket_id,),
    )
