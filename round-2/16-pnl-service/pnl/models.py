from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Fill:
    fill_id: int
    book: str
    security: str
    currency: str
    side: str
    quantity: Decimal
    price: Decimal
    trade_date: date


@dataclass
class Lot:
    opened: date
    quantity: Decimal
    cost: Decimal  # per share


@dataclass(frozen=True)
class Split:
    security: str
    effective: date
    ratio: Decimal
