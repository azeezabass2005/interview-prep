import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    role        TEXT NOT NULL,
    team        TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS expenses (
    expense_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id   TEXT NOT NULL,
    amount        TEXT NOT NULL,
    currency      TEXT NOT NULL,
    expense_date  TEXT NOT NULL,
    description   TEXT NOT NULL,
    status        TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id  INTEGER NOT NULL,
    approver_id TEXT NOT NULL,
    from_status TEXT NOT NULL,
    to_status   TEXT NOT NULL,
    at          TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS payments (
    payment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id  INTEGER NOT NULL,
    amount_usd  TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fx_rates (
    currency    TEXT NOT NULL,
    rate_date   TEXT NOT NULL,
    usd_per_unit TEXT NOT NULL,
    PRIMARY KEY (currency, rate_date)
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
