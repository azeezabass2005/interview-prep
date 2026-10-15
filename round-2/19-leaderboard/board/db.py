import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS participants (
    participant_id TEXT PRIMARY KEY,
    name           TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS totals (
    participant_id TEXT PRIMARY KEY,
    score          INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS weekly_totals (
    participant_id TEXT NOT NULL,
    week_start     TEXT NOT NULL,
    score          INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (participant_id, week_start)
);
CREATE TABLE IF NOT EXISTS score_events (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id TEXT NOT NULL,
    points         INTEGER NOT NULL,
    at             TEXT NOT NULL
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
