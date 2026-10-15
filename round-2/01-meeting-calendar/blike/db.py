import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS meeting_requests (
    request_id        TEXT PRIMARY KEY,
    requester         TEXT NOT NULL,
    idempotency_key   TEXT NOT NULL,
    title             TEXT NOT NULL,
    sender            TEXT NOT NULL,
    duration_minutes  INTEGER NOT NULL,
    urgency           TEXT NOT NULL,
    earliest          TEXT NOT NULL,
    latest            TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    score             INTEGER NOT NULL DEFAULT 0,
    status            TEXT NOT NULL DEFAULT 'PENDING'
);
-- lookups for client retries
CREATE INDEX IF NOT EXISTS idx_requests_requester_key ON meeting_requests (requester, idempotency_key);
CREATE INDEX IF NOT EXISTS idx_requests_status ON meeting_requests (status);

CREATE TABLE IF NOT EXISTS commitments (
    commitment_id TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    start         TEXT NOT NULL,
    end           TEXT NOT NULL,
    protected     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS meetings (
    meeting_id  TEXT PRIMARY KEY,
    request_id  TEXT NOT NULL REFERENCES meeting_requests (request_id),
    title       TEXT NOT NULL,
    start       TEXT NOT NULL,
    end         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outbox (
    message_id  TEXT PRIMARY KEY,
    recipient   TEXT NOT NULL,
    subject     TEXT NOT NULL,
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    sent        INTEGER NOT NULL DEFAULT 0
);
"""


class Database:
    """Thin wrapper around a SQLite file. Each transaction uses its own connection."""

    def __init__(self, path: str):
        self.path = path

    def initialize(self) -> None:
        with self.transaction() as conn:
            conn.executescript(SCHEMA)

    @contextlib.contextmanager
    def transaction(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
