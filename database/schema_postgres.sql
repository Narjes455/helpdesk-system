-- مخطط قاعدة البيانات — نسخة PostgreSQL (الإنتاج / Neon)

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('employee', 'technician', 'manager')),
    department    TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tickets (
    id           SERIAL PRIMARY KEY,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL,
    category     TEXT NOT NULL,
    priority     TEXT NOT NULL CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    status       TEXT NOT NULL DEFAULT 'new'
                 CHECK (status IN ('new', 'in_review', 'in_progress', 'waiting_user', 'closed')),
    created_by   INTEGER NOT NULL REFERENCES users(id),
    assigned_to  INTEGER REFERENCES users(id),
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    first_response_at TIMESTAMP,
    closed_at    TIMESTAMP,
    due_at       TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS action_logs (
    id         SERIAL PRIMARY KEY,
    ticket_id  INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    action     TEXT NOT NULL,
    note       TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned ON tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_logs_ticket ON action_logs(ticket_id);
