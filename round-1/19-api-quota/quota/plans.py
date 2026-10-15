from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Plan:
    name: str
    capacity: Decimal
    refill_per_second: Decimal


PLANS = {
    "FREE": Plan("FREE", Decimal(10), Decimal(1)),
    "PRO": Plan("PRO", Decimal(100), Decimal(20)),
    "ENTERPRISE": Plan("ENTERPRISE", Decimal(1000), Decimal(200)),
}

ENDPOINT_COST = {"/quote": 1, "/history": 5, "/bulk": 20}
