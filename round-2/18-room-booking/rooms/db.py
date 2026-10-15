import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
    room_id   TEXT PRIMARY KEY,
    name      TEXT NOT NULL,
    capacity  INTEGER NOT NULL,
    timezone  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
    booking_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id     TEXT NOT NULL,
    organizer   TEXT NOT NULL,
    attendees   TEXT NOT NULL,
    start       TEXT NOT NULL,
    end         TEXT NOT NULL,
    series_id   TEXT
);
CREATE INDEX IF NOT EXISTS idx_bookings_room_start ON bookings (room_id, start);
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
