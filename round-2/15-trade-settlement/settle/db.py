import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS trades (
    trade_id     TEXT PRIMARY KEY,
    account      TEXT NOT NULL,
    security     TEXT NOT NULL,
    asset_class  TEXT NOT NULL,
    side         TEXT NOT NULL,
    quantity     INTEGER NOT NULL,
    price        TEXT NOT NULL,
    trade_date   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS confirms (
    broker_ref  TEXT PRIMARY KEY,
    trade_id    TEXT NOT NULL,
    side        TEXT NOT NULL,
    quantity    INTEGER NOT NULL,
    price       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS instructions (
    instruction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    account         TEXT NOT NULL,
    security        TEXT NOT NULL,
    settle_date     TEXT NOT NULL,
    net_quantity    INTEGER NOT NULL,
    net_cash        TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS instruction_trades (
    instruction_id  INTEGER NOT NULL,
    trade_id        TEXT NOT NULL
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
