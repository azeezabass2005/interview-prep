from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Plan:
    name: str
    capacity: Decimal
    refill_per_second: Decimal
    allowance: int
    monthly_fee: Decimal
    overage_price: Decimal
    hard_cap: bool


PLANS = {
    "FREE": Plan("FREE", Decimal(10), Decimal(1), 10_000, Decimal("0"), Decimal("0"), True),
    "PRO": Plan("PRO", Decimal(100), Decimal(20), 1_000_000, Decimal("500"), Decimal("0.001"), False),
}
COSTS = {"/quote": 1, "/history": 5, "/bulk": 20}
