from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Reading:
    month: date  # first day of the billed month
    consumed_kwh: int
    exported_kwh: int


@dataclass(frozen=True)
class Bill:
    month: date
    billable_kwh: int
    energy: Decimal
    tax: Decimal
    fixed: Decimal
    total: Decimal
    true_up_payout: Decimal = Decimal("0.00")
