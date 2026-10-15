from datetime import datetime
from typing import Optional

from ..db import Database
from ..models import Order


class OrderRepository:
    def __init__(self, db: Database):
        self._db = db

    def insert(self, o: Order, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (o.order_id, o.event_id, o.customer, ",".join(o.seat_ids), o.face_total_cents, o.fee_total_cents,
                 o.total_cents, o.status, at.isoformat()),
            )

    def get(self, order_id: str) -> Optional[Order]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        if r is None:
            return None
        return Order(r["order_id"], r["event_id"], r["customer"], tuple(r["seat_ids"].split(",")),
                     r["face_total_cents"], r["fee_total_cents"], r["total_cents"], r["status"])

    def set_status(self, order_id: str, status: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))

    def sold_for_event(self, event_id: str):
        with self._db.transaction() as conn:
            return conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(total_cents), 0) FROM orders WHERE event_id = ? AND status = 'PAID'",
                (event_id,)).fetchone()
