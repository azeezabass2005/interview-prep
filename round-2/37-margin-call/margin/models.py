from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

OPEN, MET = "OPEN", "MET"


@dataclass(frozen=True)
class Price:
    symbol: str
    on: date
    price: Decimal


@dataclass
class Account:
    account_id: str
    cash: Decimal
    positions: Dict[str, int] = field(default_factory=dict)


@dataclass
class Call:
    account_id: str
    issued_on: date
    amount: Decimal
    status: str = OPEN


@dataclass(frozen=True)
class Deposit:
    account_id: str
    on: date
    amount: Decimal


@dataclass(frozen=True)
class Line:
    symbol: str
    quantity: int
    price: Decimal
    market_value: Decimal
    haircut: Optional[Decimal]
