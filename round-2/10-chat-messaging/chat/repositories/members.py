from ..db import Database


class MemberRepository:
    def __init__(self, db: Database):
        self._db = db

    def last_read(self, conversation_id: str, user_id: str) -> int:
        with self._db.transaction() as conn:
            row = conn.execute("SELECT last_read_seq FROM members WHERE conversation_id = ? AND user_id = ?",
                               (conversation_id, user_id)).fetchone()
        return row[0] if row else 0

    def set_last_read(self, conversation_id: str, user_id: str, seq: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE members SET last_read_seq = ? WHERE conversation_id = ? AND user_id = ?",
                         (seq, conversation_id, user_id))
