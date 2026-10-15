from datetime import date, datetime, time, timedelta
from typing import List

from ..db import Database
from ..errors import NotFound
from ..models import Booking
from ..repositories.bookings import BookingRepository
from ..repositories.rooms import RoomRepository


class AvailabilityService:
    def __init__(self, db: Database):
        self._rooms = RoomRepository(db)
        self._bookings = BookingRepository(db)

    def day_schedule(self, room_id: str, local_day: date) -> List[Booking]:
        room = self._rooms.get(room_id)
        if room is None:
            raise NotFound(room_id)
        day_start = datetime.combine(local_day, time.min)
        return self._bookings.starting_between(room_id, day_start, day_start + timedelta(days=1))
