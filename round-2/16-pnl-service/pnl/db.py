import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS fills (
    fill_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    book        TEXT NOT NULL,
    security    TEXT NOT NULL,
    currency    TEXT NOT NULL,
    side        TEXT NOT NULL,
    quantity    TEXT NOT NULL,
    price       TEXT NOT NULL,
    trade_date  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS prices (
    security    TEXT NOT NULL,
    price_date  TEXT NOT NULL,
    close       TEXT NOT NULL,
    PRIMARY KEY (security, price_date)
);
CREATE TABLE IF NOT EXISTS splits (
    security   TEXT NOT NULL,
    effective  TEXT NOT NULL,
    ratio      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fx_rates (
    currency      TEXT NOT NULL,
    rate_date     TEXT NOT NULL,
    usd_per_unit  TEXT NOT NULL,
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
