"""عمليات المستخدمين."""

from database.connection import execute, query_all, query_one
from utils.auth import hash_password, verify_password


def create_user(name: str, email: str, password: str, role: str, department: str = "") -> int:
    """إضافة مستخدم جديد وإرجاع معرّفه."""
    return execute(
        """INSERT INTO users (name, email, password_hash, role, department)
           VALUES (?, ?, ?, ?, ?)""",
        (name, email.strip().lower(), hash_password(password), role, department),
    )


def authenticate(email: str, password: str) -> dict | None:
    """التحقق من بيانات الدخول وإرجاع بيانات المستخدم عند النجاح."""
    user = query_one(
        "SELECT * FROM users WHERE email = ? AND is_active = 1",
        (email.strip().lower(),),
    )
    if user and verify_password(password, user["password_hash"]):
        user.pop("password_hash", None)
        return user
    return None


def get_user(user_id: int) -> dict | None:
    return query_one("SELECT id, name, email, role, department FROM users WHERE id = ?", (user_id,))


def list_users(role: str | None = None) -> list:
    """قائمة المستخدمين، مع إمكانية التصفية حسب الدور."""
    if role:
        return query_all(
            "SELECT id, name, email, role, department, is_active FROM users "
            "WHERE role = ? ORDER BY name",
            (role,),
        )
    return query_all(
        "SELECT id, name, email, role, department, is_active FROM users ORDER BY name"
    )


def email_exists(email: str) -> bool:
    return query_one("SELECT id FROM users WHERE email = ?", (email.strip().lower(),)) is not None


def set_active(user_id: int, active: bool) -> None:
    execute("UPDATE users SET is_active = ? WHERE id = ?", (1 if active else 0, user_id))


def change_password(user_id: int, new_password: str) -> None:
    execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (hash_password(new_password), user_id),
    )
