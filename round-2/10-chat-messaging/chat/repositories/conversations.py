from ..db import Database


class ConversationRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, conversation_id: str, title: str, members) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO conversations (conversation_id, title) VALUES (?, ?)", (conversation_id, title))
            conn.executemany("INSERT INTO members (conversation_id, user_id) VALUES (?, ?)",
                             [(conversation_id, m) for m in members])

    def is_member(self, conversation_id: str, user_id: str) -> bool:
        with self._db.transaction() as conn:
            return conn.execute("SELECT 1 FROM members WHERE conversation_id = ? AND user_id = ?",
                                (conversation_id, user_id)).fetchone() is not None

    def next_seq(self, conversation_id: str) -> int:
        with self._db.transaction() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("UPDATE conversations SET last_seq = last_seq + 1 WHERE conversation_id = ?", (conversation_id,))
            return conn.execute("SELECT last_seq FROM conversations WHERE conversation_id = ?",
                                (conversation_id,)).fetchone()[0]
