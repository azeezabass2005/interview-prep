import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    event_id         TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    venue_tz         TEXT NOT NULL,
    starts_at_local  TEXT NOT NULL,
    face_value_cents INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS seats (
    event_id         TEXT NOT NULL,
    seat_id          TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'AVAILABLE',
    held_by          TEXT,
    hold_expires_at  TEXT,
    order_id         TEXT,
    PRIMARY KEY (event_id, seat_id)
);
CREATE TABLE IF NOT EXISTS orders (
    order_id         TEXT PRIMARY KEY,
    event_id         TEXT NOT NULL,
    customer         TEXT NOT NULL,
    seat_ids         TEXT NOT NULL,
    face_total_cents INTEGER NOT NULL,
    fee_total_cents  INTEGER NOT NULL,
    total_cents      INTEGER NOT NULL,
    status           TEXT NOT NULL,
    created_at       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient  TEXT NOT NULL,
    subject    TEXT NOT NULL,
    created_at TEXT NOT NULL
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
