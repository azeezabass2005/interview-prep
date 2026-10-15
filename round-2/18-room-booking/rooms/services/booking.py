import uuid
from datetime import date, datetime, timedelta
from typing import List, Sequence

from ..config import MAX_BOOKING_HOURS, MAX_SERIES_OCCURRENCES
from ..db import Database
from ..errors import Conflict, NotFound, RoomError
from ..repositories.bookings import BookingRepository
from ..repositories.rooms import RoomRepository


class BookingService:
    def __init__(self, db: Database):
        self._rooms = RoomRepository(db)
        self._bookings = BookingRepository(db)

    def _validate(self, room_id: str, attendees: Sequence[str], start: datetime, end: datetime):
        room = self._rooms.get(room_id)
        if room is None:
            raise NotFound(room_id)
        if end <= start or end - start > timedelta(hours=MAX_BOOKING_HOURS):
            raise RoomError("bookings must be between 1 minute and 10 hours")
        if len(attendees) > room.capacity:
            raise RoomError(f"{room.name} holds {room.capacity} people")
        return room

    def book(self, room_id: str, organizer: str, attendees: Sequence[str], start: datetime, end: datetime,
             series_id=None) -> int:
        self._validate(room_id, attendees, start, end)
        if self._bookings.overlapping(room_id, start, end):
            raise Conflict("room is already booked")
        return self._bookings.insert(room_id, organizer, attendees, start, end, series_id)

    def book_weekly(self, room_id: str, organizer: str, attendees: Sequence[str], first_start: datetime,
                    duration: timedelta, until: date) -> List[int]:
        series_id = f"ser_{uuid.uuid4().hex[:8]}"
        ids, start = [], first_start
        while start.date() < until and len(ids) < MAX_SERIES_OCCURRENCES:
            ids.append(self.book(room_id, organizer, attendees, start, start + duration, series_id))
            start += timedelta(days=7)
        return ids
