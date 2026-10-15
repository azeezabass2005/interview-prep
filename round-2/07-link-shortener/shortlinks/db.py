import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
    code        TEXT PRIMARY KEY,
    target_url  TEXT NOT NULL,
    owner       TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    expires_at  TEXT,
    clicks      INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS click_events (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    code      TEXT NOT NULL,
    at        TEXT NOT NULL,
    referrer  TEXT
);
CREATE INDEX IF NOT EXISTS idx_clicks_code ON click_events (code);
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
