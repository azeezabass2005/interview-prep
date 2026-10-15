import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id     TEXT PRIMARY KEY,
    owner          TEXT NOT NULL,
    balance_cents  INTEGER NOT NULL DEFAULT 0,
    status         TEXT NOT NULL DEFAULT 'OPEN'
);
CREATE TABLE IF NOT EXISTS entries (
    entry_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id    TEXT NOT NULL REFERENCES accounts (account_id),
    amount_cents  INTEGER NOT NULL,
    kind          TEXT NOT NULL,
    reference     TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entries_account_time ON entries (account_id, created_at);
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
