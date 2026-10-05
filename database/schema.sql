-- مخطط قاعدة البيانات — نسخة SQLite (التطوير المحلي)

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('employee', 'technician', 'manager')),
    department    TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tickets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL,
    category     TEXT NOT NULL,
    priority     TEXT NOT NULL CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    status       TEXT NOT NULL DEFAULT 'new'
                 CHECK (status IN ('new', 'in_review', 'in_progress', 'waiting_user', 'closed')),
    created_by   INTEGER NOT NULL REFERENCES users(id),
    assigned_to  INTEGER REFERENCES users(id),
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    first_response_at TEXT,
    closed_at    TEXT,
    due_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS action_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id  INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    action     TEXT NOT NULL,
    note       TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned ON tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_logs_ticket ON action_logs(ticket_id);
