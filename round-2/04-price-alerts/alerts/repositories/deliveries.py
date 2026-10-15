from datetime import datetime
from typing import List

from ..db import Database
from ..models import Delivery


def _to_delivery(r) -> Delivery:
    return Delivery(r["delivery_id"], r["alert_id"], r["user_id"], r["message"],
                    datetime.fromisoformat(r["deliver_after"]), r["status"])


class DeliveryRepository:
    def __init__(self, db: Database):
        self._db = db

    def enqueue(self, alert_id: int, user_id: str, message: str, deliver_after: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO deliveries (alert_id, user_id, message, deliver_after) VALUES (?, ?, ?, ?)",
                (alert_id, user_id, message, deliver_after.isoformat()),
            )

    def pending_due(self, now: datetime, limit: int) -> List[Delivery]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM deliveries WHERE status = 'PENDING' AND deliver_after <= ? ORDER BY delivery_id LIMIT ?",
                (now.isoformat(), limit),
            ).fetchall()
        return [_to_delivery(r) for r in rows]

    def get(self, delivery_id: int) -> Delivery:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM deliveries WHERE delivery_id = ?", (delivery_id,)).fetchone()
        return _to_delivery(r)

    def mark_sent(self, delivery_id: int, worker_id: str, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE deliveries SET status = 'SENT', sent_by = ?, sent_at = ? WHERE delivery_id = ?",
                         (worker_id, at.isoformat(), delivery_id))

    def all(self) -> List[Delivery]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM deliveries ORDER BY delivery_id").fetchall()
        return [_to_delivery(r) for r in rows]
