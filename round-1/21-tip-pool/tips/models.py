from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class Shift:
    employee: str
    role: str
    start: datetime
    end: datetime


@dataclass(frozen=True)
class Declaration:
    day: date
    service: str
    card: Decimal
    cash: Decimal
