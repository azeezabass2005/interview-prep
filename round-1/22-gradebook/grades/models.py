from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Item:
    category: str
    name: str
    points: Optional[Decimal]  # None = missing
    max_points: Decimal
    days_late: Decimal = Decimal(0)
    excused: bool = False
