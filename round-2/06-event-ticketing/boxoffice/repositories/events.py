from datetime import datetime
from typing import Optional

from ..db import Database
from ..models import Event


class EventRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, e: Event, seat_ids) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?)",
                         (e.event_id, e.name, e.venue_tz, e.starts_at_local.isoformat(), e.face_value_cents))
            conn.executemany("INSERT INTO seats (event_id, seat_id) VALUES (?, ?)", [(e.event_id, s) for s in seat_ids])

    def get(self, event_id: str) -> Optional[Event]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
        if r is None:
            return None
        return Event(r["event_id"], r["name"], r["venue_tz"], datetime.fromisoformat(r["starts_at_local"]),
                     r["face_value_cents"])
