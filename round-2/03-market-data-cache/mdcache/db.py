import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS official_closes (
    symbol      TEXT NOT NULL,
    trade_date  TEXT NOT NULL,
    close       TEXT NOT NULL,
    recorded_at REAL NOT NULL,
    PRIMARY KEY (symbol, trade_date)
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
