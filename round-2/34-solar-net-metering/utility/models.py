from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class Reading:
    read_on: date
    import_register: int
    export_register: int


@dataclass(frozen=True)
class Bill:
    period_start: date
    period_end: date
    days: int
    imported: int
    exported: int
    billable_kwh: int
    energy: Decimal
    tax: Decimal
    service: Decimal
    total: Decimal
    true_up_payout: Decimal = Decimal("0.00")


@dataclass
class Account:
    account_id: str
    address: str
    readings: List[Reading] = field(default_factory=list)
    bills: List[Bill] = field(default_factory=list)
    bank_kwh: int = 0
