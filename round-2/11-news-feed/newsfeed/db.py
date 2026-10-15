import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS stories (
    story_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_url  TEXT NOT NULL UNIQUE,
    original_url   TEXT NOT NULL,
    headline       TEXT NOT NULL,
    source         TEXT NOT NULL,
    published_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_stories_published ON stories (published_at);
CREATE TABLE IF NOT EXISTS story_tags (
    story_id  INTEGER NOT NULL,
    tag       TEXT NOT NULL,
    PRIMARY KEY (story_id, tag)
);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON story_tags (tag);
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
