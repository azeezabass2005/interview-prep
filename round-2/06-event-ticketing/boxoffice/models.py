from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

AVAILABLE, HELD, SOLD = "AVAILABLE", "HELD", "SOLD"


@dataclass(frozen=True)
class Event:
    event_id: str
    name: str
    venue_tz: str
    starts_at_local: datetime  # naive, venue local time
    face_value_cents: int


@dataclass(frozen=True)
class Seat:
    event_id: str
    seat_id: str
    status: str
    held_by: Optional[str]
    hold_expires_at: Optional[str]  # ISO string as stored
    order_id: Optional[str]


@dataclass(frozen=True)
class Order:
    order_id: str
    event_id: str
    customer: str
    seat_ids: Tuple[str, ...]
    face_total_cents: int
    fee_total_cents: int
    total_cents: int
    status: str
