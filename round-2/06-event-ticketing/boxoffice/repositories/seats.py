from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import Seat


def _to_seat(r) -> Seat:
    return Seat(r["event_id"], r["seat_id"], r["status"], r["held_by"], r["hold_expires_at"], r["order_id"])


class SeatRepository:
    def __init__(self, db: Database):
        self._db = db

    def get(self, event_id: str, seat_id: str) -> Optional[Seat]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM seats WHERE event_id = ? AND seat_id = ?", (event_id, seat_id)).fetchone()
        return _to_seat(r) if r else None

    def for_event(self, event_id: str) -> List[Seat]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM seats WHERE event_id = ? ORDER BY seat_id", (event_id,)).fetchall()
        return [_to_seat(r) for r in rows]

    def set_hold(self, event_id: str, seat_id: str, customer: str, expires_at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "UPDATE seats SET status = 'HELD', held_by = ?, hold_expires_at = ? WHERE event_id = ? AND seat_id = ?",
                (customer, expires_at.isoformat(), event_id, seat_id),
            )

    def mark_sold(self, event_id: str, seat_ids, order_id: str) -> None:
        with self._db.transaction() as conn:
            conn.executemany(
                "UPDATE seats SET status = 'SOLD', order_id = ?, hold_expires_at = NULL WHERE event_id = ? AND seat_id = ?",
                [(order_id, event_id, s) for s in seat_ids],
            )

    def release(self, event_id: str, seat_ids) -> None:
        with self._db.transaction() as conn:
            conn.executemany(
                "UPDATE seats SET status = 'AVAILABLE', held_by = NULL, hold_expires_at = NULL, order_id = NULL "
                "WHERE event_id = ? AND seat_id = ?",
                [(event_id, s) for s in seat_ids],
            )
