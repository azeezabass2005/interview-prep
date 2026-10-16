from collections import deque
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Deque, Optional, Set


@dataclass
class Branch:
    code: str
    holidays: Set[date] = field(default_factory=set)


@dataclass
class Item:
    barcode: str
    kind: str
    branch: str
    holds: Deque[str] = field(default_factory=deque)
    on_hold_for: Optional[str] = None


@dataclass
class Loan:
    barcode: str
    patron: str
    branch: str
    kind: str
    borrowed_on: date
    due_on: date
    renewals: int = 0
    returned_on: Optional[date] = None
    fine: Decimal = Decimal("0.00")


@dataclass
class Patron:
    patron_id: str
    balance: Decimal = Decimal("0.00")
