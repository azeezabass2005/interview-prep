import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS flags (
    key              TEXT PRIMARY KEY,
    enabled          INTEGER NOT NULL DEFAULT 1,
    rollout_percent  INTEGER NOT NULL DEFAULT 0,
    archived         INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS flag_overrides (
    flag_key  TEXT NOT NULL,
    user_id   TEXT NOT NULL,
    value     INTEGER NOT NULL,
    PRIMARY KEY (flag_key, user_id)
);
CREATE TABLE IF NOT EXISTS flag_rules (
    flag_key   TEXT NOT NULL,
    position   INTEGER NOT NULL,
    attribute  TEXT NOT NULL,
    equals     TEXT NOT NULL,
    value      INTEGER NOT NULL,
    PRIMARY KEY (flag_key, position)
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
