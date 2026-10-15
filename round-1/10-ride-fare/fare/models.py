from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Trip:
    trip_id: str
    zone: str
    miles: Decimal
    duration_seconds: int
    quoted_surge: Decimal  # multiplier shown when the rider requested the ride
    tolls: Decimal = Decimal("0")
