from datetime import datetime
from typing import List

from ..db import Database
from ..models import Reservation


def _to_res(r) -> Reservation:
    return Reservation(r["reservation_id"], r["cart_id"], r["sku"], r["qty"],
                       datetime.fromisoformat(r["expires_at"]), r["status"])


class ReservationRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, cart_id: str, sku: str, qty: int, expires_at: datetime) -> int:
        with self._db.transaction() as conn:
            cur = conn.execute("INSERT INTO reservations (cart_id, sku, qty, expires_at) VALUES (?, ?, ?, ?)",
                               (cart_id, sku, qty, expires_at.isoformat()))
            return cur.lastrowid

    def active_for_cart(self, cart_id: str) -> List[Reservation]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM reservations WHERE cart_id = ? AND status = 'ACTIVE'",
                                (cart_id,)).fetchall()
        return [_to_res(r) for r in rows]

    def expired(self, now: datetime) -> List[Reservation]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM reservations WHERE status = 'ACTIVE' AND expires_at < ?",
                                (now.isoformat(),)).fetchall()
        return [_to_res(r) for r in rows]

    def set_status(self, reservation_id: int, status: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE reservations SET status = ? WHERE reservation_id = ?", (status, reservation_id))

    def active_total(self, sku: str) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COALESCE(SUM(qty), 0) FROM reservations WHERE sku = ? AND status = 'ACTIVE'",
                                (sku,)).fetchone()[0]
