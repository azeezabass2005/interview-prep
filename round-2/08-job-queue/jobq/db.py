import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    kind              TEXT NOT NULL,
    payload           TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'PENDING',
    attempts          INTEGER NOT NULL DEFAULT 0,
    max_attempts      INTEGER NOT NULL,
    run_at            TEXT NOT NULL,
    lease_owner       TEXT,
    claimed_at        TEXT,
    lease_expires_at  TEXT,
    last_error        TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_due ON jobs (status, run_at);
CREATE TABLE IF NOT EXISTS job_runs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id    INTEGER NOT NULL,
    worker    TEXT NOT NULL,
    started   TEXT NOT NULL,
    outcome   TEXT
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
