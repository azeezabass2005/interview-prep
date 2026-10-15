from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass(frozen=True)
class Room:
    room_id: str
    name: str
    capacity: int
    timezone: str


@dataclass(frozen=True)
class Booking:
    booking_id: int
    room_id: str
    organizer: str
    attendees: Tuple[str, ...]
    start: datetime  # naive UTC
    end: datetime  # naive UTC
    series_id: Optional[str] = None
