FIXES = [
    ("chat/repositories/messages.py",
     "\"SELECT * FROM messages WHERE conversation_id = ? ORDER BY client_sent_at DESC LIMIT ?\"",
     "\"SELECT * FROM messages WHERE conversation_id = ? ORDER BY seq DESC LIMIT ?\""),
    ("chat/repositories/messages.py",
     """                "SELECT * FROM messages WHERE conversation_id = ? AND seq < ? ORDER BY seq ASC LIMIT ?",
                (conversation_id, before_seq, limit)).fetchall()
        return [_to_msg(r) for r in rows]""",
     """                "SELECT * FROM messages WHERE conversation_id = ? AND seq < ? ORDER BY seq DESC LIMIT ?",
                (conversation_id, before_seq, limit)).fetchall()
        return list(reversed([_to_msg(r) for r in rows]))"""),
    ("chat/repositories/members.py",
     "\"UPDATE members SET last_read_seq = ? WHERE conversation_id = ? AND user_id = ?\"",
     "\"UPDATE members SET last_read_seq = MAX(last_read_seq, ?) WHERE conversation_id = ? AND user_id = ?\""),
    ("chat/db.py", "CREATE INDEX IF NOT EXISTS idx_messages_client", "CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_client"),
    ("chat/repositories/messages.py",
     "    def insert(self, m: Message) -> None:",
     """    def insert_with_next_seq(self, m: Message) -> Message:
        \"\"\"Allocate the next seq and insert in one transaction; return the existing message on a retry.\"\"\"
        with self._db.transaction() as conn:
            conn.execute("BEGIN IMMEDIATE")
            r = conn.execute("SELECT * FROM messages WHERE conversation_id = ? AND sender = ? AND client_msg_id = ?",
                             (m.conversation_id, m.sender, m.client_msg_id)).fetchone()
            if r is not None:
                return _to_msg(r)
            conn.execute("UPDATE conversations SET last_seq = last_seq + 1 WHERE conversation_id = ?", (m.conversation_id,))
            seq = conn.execute("SELECT last_seq FROM conversations WHERE conversation_id = ?",
                               (m.conversation_id,)).fetchone()[0]
            conn.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (m.message_id, m.conversation_id, seq, m.sender, m.body, m.client_msg_id,
                          m.client_sent_at.isoformat(), m.received_at.isoformat()))
        return Message(m.message_id, m.conversation_id, seq, m.sender, m.body, m.client_msg_id,
                       m.client_sent_at, m.received_at)

    def insert(self, m: Message) -> None:"""),
    ("chat/services/messaging.py",
     """        seq = self._conversations.next_seq(conversation_id)
        message = Message(f"msg_{uuid.uuid4().hex[:12]}", conversation_id, seq, sender, mask(body), client_msg_id,
                          client_sent_at, self._clock.now())
        self._messages.insert(message)
        return message""",
     """        message = Message(f"msg_{uuid.uuid4().hex[:12]}", conversation_id, 0, sender, mask(body), client_msg_id,
                          client_sent_at, self._clock.now())
        return self._messages.insert_with_next_seq(message)"""),
]
