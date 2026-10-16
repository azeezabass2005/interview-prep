import json

from .db import Database


class AuditLog:

    def __init__(self, db: Database, clock):
        self._db = db
        self._clock = clock

    def record(self, order_id: str, event: str, **detail) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO audit_log (order_id, event, detail, at) VALUES (?, ?, ?, ?)",
                         (order_id, event, json.dumps(detail, default=str), self._clock.now().isoformat()))

    def events_for(self, order_id: str):
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT event FROM audit_log WHERE order_id = ? ORDER BY id", (order_id,)).fetchall()
        return [r["event"] for r in rows]
