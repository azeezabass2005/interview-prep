import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id     TEXT PRIMARY KEY,
    account      TEXT NOT NULL,
    symbol       TEXT NOT NULL,
    side         TEXT NOT NULL,
    quantity     INTEGER NOT NULL,
    limit_price  TEXT NOT NULL,
    status       TEXT NOT NULL,
    filled_qty   INTEGER NOT NULL DEFAULT 0,
    avg_price    TEXT,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_account ON orders (account, symbol);

CREATE TABLE IF NOT EXISTS executions (
    exec_id      TEXT PRIMARY KEY,
    order_id     TEXT NOT NULL REFERENCES orders (order_id),
    quantity     INTEGER NOT NULL,
    price        TEXT NOT NULL,
    executed_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_exec_order ON executions (order_id);

CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   TEXT NOT NULL,
    event      TEXT NOT NULL,
    detail     TEXT NOT NULL,
    at         TEXT NOT NULL
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
