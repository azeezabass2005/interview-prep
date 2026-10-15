from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Shift:
    employee: str
    role: str
    hours: Decimal


@dataclass(frozen=True)
class NightTips:
    card: Decimal
    cash: Decimal
