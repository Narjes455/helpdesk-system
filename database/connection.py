"""طبقة الاتصال بقاعدة البيانات.

تدعم وضعين:
  - SQLite  (الوضع الافتراضي) — يعمل مباشرة بدون أي إعداد، مناسب للتطوير المحلي.
  - PostgreSQL — للإنتاج (مثل Neon.tech)، يُفعّل بضبط متغير البيئة DATABASE_URL.

الاختيار يتم تلقائيًا: إذا وُجد DATABASE_URL نستخدم PostgreSQL، وإلا SQLite.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SQLITE_PATH = BASE_DIR / "helpdesk.db"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

IS_POSTGRES = bool(DATABASE_URL)


def _adapt(sql: str) -> str:
    """تحويل علامات الاستفهام إلى %s عند استخدام PostgreSQL."""
    if IS_POSTGRES:
        return sql.replace("?", "%s")
    return sql


@contextmanager
def get_connection():
    """فتح اتصال وإغلاقه تلقائيًا مع commit عند النجاح و rollback عند الخطأ."""
    if IS_POSTGRES:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_all(sql: str, params: tuple = ()) -> list:
    """تنفيذ استعلام وإرجاع كل الصفوف كقائمة قواميس."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(_adapt(sql), params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]


def query_one(sql: str, params: tuple = ()):
    """تنفيذ استعلام وإرجاع أول صف أو None."""
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple = ()) -> int:
    """تنفيذ أمر INSERT/UPDATE/DELETE وإرجاع معرّف الصف الجديد إن وُجد."""
    with get_connection() as conn:
        cur = conn.cursor()
        if IS_POSTGRES and sql.strip().upper().startswith("INSERT"):
            cur.execute(_adapt(sql) + " RETURNING id", params)
            row = cur.fetchone()
            return row["id"] if row else 0
        cur.execute(_adapt(sql), params)
        return cur.lastrowid or 0


def init_database() -> None:
    """إنشاء الجداول إن لم تكن موجودة."""
    schema_file = "schema_postgres.sql" if IS_POSTGRES else "schema.sql"
    schema_path = Path(__file__).resolve().parent / schema_file
    script = schema_path.read_text(encoding="utf-8")

    with get_connection() as conn:
        cur = conn.cursor()
        for statement in script.split(";"):
            if statement.strip():
                cur.execute(statement)


def database_label() -> str:
    """وصف مختصر لنوع قاعدة البيانات المستخدمة حاليًا (يظهر في الواجهة)."""
    return "PostgreSQL (سحابي)" if IS_POSTGRES else "SQLite (محلي)"
