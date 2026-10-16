from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

FLIGHT, TRANSFER = "FLIGHT", "TRANSFER"


@dataclass(frozen=True)
class Member:
    member_id: str
    name: str


@dataclass
class Flight:
    flight_id: str
    member_id: str
    flown_on: date
    base_fare: Decimal
    base_miles: int = 0
    bonus_miles: int = 0
    cancelled: bool = False


@dataclass
class Lot:
    lot_id: int
    member_id: str
    dated: date
    miles: int
    remaining: int
    source: str
    flight_id: Optional[str] = None
