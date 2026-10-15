from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

PURCHASE = "PURCHASE"
CASH = "CASH"
PAYMENT = "PAYMENT"


@dataclass(frozen=True)
class Txn:
    day: int  # 0-based day within the cycle
    kind: str
    amount: Decimal


@dataclass
class Cycle:
    days: int
    paid_in_full_last_cycle: bool
    start_purchase: Decimal = Decimal("0")
    start_cash: Decimal = Decimal("0")
    txns: List[Txn] = field(default_factory=list)


@dataclass(frozen=True)
class Statement:
    purchase_balance: Decimal
    cash_balance: Decimal
    purchase_interest: Decimal
    cash_interest: Decimal
    new_balance: Decimal
    minimum_due: Decimal
