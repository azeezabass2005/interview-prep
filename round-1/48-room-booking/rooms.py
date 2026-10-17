import itertools
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

OPEN = time(7, 0)
CLOSE = time(20, 0)
MAX_LENGTH = timedelta(hours=4)
CHECK_IN_WINDOW = timedelta(minutes=10)


class BookingError(Exception):
    pass


@dataclass
class Room:
    name: str
    tz: ZoneInfo
    capacity: int


@dataclass
class Booking:
    booking_id: int
    room: str
    start: datetime
    end: datetime
    organizer: str
    checked_in: bool = False


class RoomService:
    def __init__(self):
        self.rooms = {}
        self.bookings = {}
        self._ids = itertools.count(1)

    def add_room(self, name, tz, capacity):
        self.rooms[name] = Room(name, ZoneInfo(tz), capacity)

    def _active(self, b, now):
        return True

    def _free(self, room, start, end, now):
        return not any(b.room == room and self._active(b, now) and b.start < end and start < b.end
                       for b in self.bookings.values())

    def _validate(self, room, start, end):
        if room not in self.rooms:
            raise BookingError("unknown room")
        if end <= start or end - start >= MAX_LENGTH:
            raise BookingError("bad length")
        if start.minute % 15 or end.minute % 15:
            raise BookingError("15-minute boundaries only")
        local_start, local_end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
        if local_start.date() != local_end.date() or local_start.time() < OPEN or local_end.time() > CLOSE:
            raise BookingError("outside opening hours")

    def book(self, room, start, end, organizer, now):
        self._validate(room, start, end)
        if not self._free(room, start, end, now):
            raise BookingError("room is taken")
        booking = Booking(next(self._ids), room, start, end, organizer)
        self.bookings[booking.booking_id] = booking
        return booking

    def book_weekly(self, room, start, end, organizer, weeks, now):
        created = []
        for week in range(weeks):
            shift = timedelta(weeks=week)
            created.append(self.book(room, start + shift, end + shift, organizer, now))
        return created

    def check_in(self, booking_id, now):
        b = self.bookings[booking_id]
        if not b.start <= now < b.start + CHECK_IN_WINDOW:
            raise BookingError("check-in window closed")
        b.checked_in = True

    def search(self, start, end, attendees, now):
        found = [r for r in self.rooms.values() if r.capacity > attendees and self._free(r.name, start, end, now)]
        return [r.name for r in sorted(found, key=lambda r: (r.capacity, r.name))]
