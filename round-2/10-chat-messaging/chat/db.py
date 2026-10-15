import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    last_seq        INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS members (
    conversation_id TEXT NOT NULL,
    user_id         TEXT NOT NULL,
    last_read_seq   INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (conversation_id, user_id)
);
CREATE TABLE IF NOT EXISTS messages (
    message_id      TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    seq             INTEGER NOT NULL,
    sender          TEXT NOT NULL,
    body            TEXT NOT NULL,
    client_msg_id   TEXT NOT NULL,
    client_sent_at  TEXT NOT NULL,
    received_at     TEXT NOT NULL,
    UNIQUE (conversation_id, seq)
);
-- retries look messages up by client id
CREATE INDEX IF NOT EXISTS idx_messages_client ON messages (conversation_id, sender, client_msg_id);
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
