from dataclasses import dataclass, field
from datetime import datetime
from typing import List

BOOKED = "BOOKED"
WAITLISTED = "WAITLISTED"


@dataclass(frozen=True)
class Member:
    member_id: str
    premium: bool = False


@dataclass(frozen=True)
class FitnessClass:
    class_id: str
    starts_at: datetime
    capacity: int


@dataclass
class ClassState:
    booked: List[Member] = field(default_factory=list)
    waitlist: List[Member] = field(default_factory=list)


class BookingError(Exception):
    pass
