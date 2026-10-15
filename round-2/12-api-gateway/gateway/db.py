import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id  TEXT PRIMARY KEY,
    plan       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS api_keys (
    api_key    TEXT PRIMARY KEY,
    tenant_id  TEXT NOT NULL,
    user_id    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rate_counters (
    bucket        TEXT NOT NULL,
    window_start  INTEGER NOT NULL,
    count         INTEGER NOT NULL,
    PRIMARY KEY (bucket, window_start)
);
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
