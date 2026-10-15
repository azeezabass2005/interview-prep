from typing import Optional

from ..db import Database
from ..models import Room


class RoomRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, room: Room) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO rooms VALUES (?, ?, ?, ?)", (room.room_id, room.name, room.capacity, room.timezone))

    def get(self, room_id: str) -> Optional[Room]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,)).fetchone()
        return Room(r["room_id"], r["name"], r["capacity"], r["timezone"]) if r else None
