import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    title    TEXT NOT NULL,
    owner    TEXT NOT NULL,
    deleted  INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS versions (
    doc_id      INTEGER NOT NULL,
    version     INTEGER NOT NULL,
    content     TEXT NOT NULL,
    checksum    TEXT NOT NULL,
    author      TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_versions_doc ON versions (doc_id, version);
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
