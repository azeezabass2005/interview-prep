SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT
);
CREATE TABLE IF NOT EXISTS rules (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('above', 'below')),
    threshold REAL NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('sms', 'email')),
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    triggered_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_rules_symbol ON rules (symbol, active);
CREATE TABLE IF NOT EXISTS deliveries (
    id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL REFERENCES rules(id),
    user_id TEXT NOT NULL REFERENCES users(id),
    channel TEXT NOT NULL,
    recipient TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued', 'sent', 'failed')),
    provider_id TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    sent_at TEXT
);
"""
