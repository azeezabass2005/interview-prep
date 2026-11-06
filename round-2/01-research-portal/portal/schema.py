SCHEMA = """
CREATE TABLE IF NOT EXISTS orgs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('client', 'internal'))
);
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES orgs(id),
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    digest_enabled INTEGER NOT NULL DEFAULT 1,
    last_digest_at TEXT
);
CREATE TABLE IF NOT EXISTS subscriptions (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES orgs(id),
    sector TEXT NOT NULL,
    starts_on TEXT NOT NULL,
    ends_on TEXT
);
CREATE INDEX IF NOT EXISTS idx_subscriptions_org ON subscriptions (org_id);
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    sector TEXT NOT NULL,
    analyst_id TEXT NOT NULL REFERENCES users(id),
    status TEXT NOT NULL CHECK (status IN ('draft', 'published', 'withdrawn')),
    summary TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL,
    published_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_reports_published ON reports (status, published_at);
CREATE TABLE IF NOT EXISTS report_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL REFERENCES reports(id),
    user_id TEXT NOT NULL REFERENCES users(id),
    read_at TEXT NOT NULL
);
"""

SECTORS = ("energy", "tech", "rates", "fx", "credit")
