import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id      TEXT PRIMARY KEY,
    timezone     TEXT NOT NULL,
    quiet_start  TEXT NOT NULL,
    quiet_end    TEXT NOT NULL,
    channel      TEXT NOT NULL DEFAULT 'push'
);
CREATE TABLE IF NOT EXISTS alerts (
    alert_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    TEXT NOT NULL REFERENCES users (user_id),
    symbol     TEXT NOT NULL,
    direction  TEXT NOT NULL,
    threshold  TEXT NOT NULL,
    active     INTEGER NOT NULL DEFAULT 1,
    armed      INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts (symbol, active);
CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id       INTEGER NOT NULL,
    user_id        TEXT NOT NULL,
    message        TEXT NOT NULL,
    deliver_after  TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'PENDING',
    sent_by        TEXT,
    sent_at        TEXT
);
CREATE INDEX IF NOT EXISTS idx_deliveries_due ON deliveries (status, deliver_after);
"""


class Database:
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
