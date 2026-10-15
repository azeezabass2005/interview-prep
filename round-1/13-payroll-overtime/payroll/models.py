from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Shift:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("shift must end after it starts")


@dataclass(frozen=True)
class Breakdown:
    regular: Decimal
    overtime: Decimal  # 1.5x
    double: Decimal  # 2x
