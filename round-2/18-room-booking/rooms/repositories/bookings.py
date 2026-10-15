from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import Booking


def _to_booking(r) -> Booking:
    return Booking(r["booking_id"], r["room_id"], r["organizer"], tuple(filter(None, r["attendees"].split(","))),
                   datetime.fromisoformat(r["start"]), datetime.fromisoformat(r["end"]), r["series_id"])


class BookingRepository:
    def __init__(self, db: Database):
        self._db = db

    def overlapping(self, room_id: str, start: datetime, end: datetime) -> List[Booking]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM bookings WHERE room_id = ? AND start < ? AND end > ?",
                                (room_id, end.isoformat(), start.isoformat())).fetchall()
        return [_to_booking(r) for r in rows]

    def insert(self, room_id: str, organizer: str, attendees, start: datetime, end: datetime,
               series_id: Optional[str] = None) -> int:
        with self._db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO bookings (room_id, organizer, attendees, start, end, series_id) VALUES (?, ?, ?, ?, ?, ?)",
                (room_id, organizer, ",".join(attendees), start.isoformat(), end.isoformat(), series_id))
            return cur.lastrowid

    def starting_between(self, room_id: str, start: datetime, end: datetime) -> List[Booking]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM bookings WHERE room_id = ? AND start >= ? AND start < ? ORDER BY start",
                                (room_id, start.isoformat(), end.isoformat())).fetchall()
        return [_to_booking(r) for r in rows]

    def count(self, room_id: str) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM bookings WHERE room_id = ?", (room_id,)).fetchone()[0]
