from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import Message


def _to_msg(r) -> Message:
    return Message(r["message_id"], r["conversation_id"], r["seq"], r["sender"], r["body"], r["client_msg_id"],
                   datetime.fromisoformat(r["client_sent_at"]), datetime.fromisoformat(r["received_at"]))


class MessageRepository:
    def __init__(self, db: Database):
        self._db = db

    def find_by_client_id(self, conversation_id: str, sender: str, client_msg_id: str) -> Optional[Message]:
        with self._db.transaction() as conn:
            r = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? AND sender = ? AND client_msg_id = ?",
                (conversation_id, sender, client_msg_id)).fetchone()
        return _to_msg(r) if r else None

    def insert(self, m: Message) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (m.message_id, m.conversation_id, m.seq, m.sender, m.body, m.client_msg_id,
                          m.client_sent_at.isoformat(), m.received_at.isoformat()))

    def recent(self, conversation_id: str, limit: int) -> List[Message]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY client_sent_at DESC LIMIT ?",
                (conversation_id, limit)).fetchall()
        return list(reversed([_to_msg(r) for r in rows]))

    def before(self, conversation_id: str, before_seq: int, limit: int) -> List[Message]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? AND seq < ? ORDER BY seq ASC LIMIT ?",
                (conversation_id, before_seq, limit)).fetchall()
        return [_to_msg(r) for r in rows]

    def count_unread(self, conversation_id: str, user_id: str, after_seq: int) -> int:
        with self._db.transaction() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM messages WHERE conversation_id = ? AND seq > ? AND sender != ?",
                (conversation_id, after_seq, user_id)).fetchone()[0]

    def count(self, conversation_id: str) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = ?", (conversation_id,)).fetchone()[0]
