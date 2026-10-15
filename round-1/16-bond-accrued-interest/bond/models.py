from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Bond:
    face: Decimal
    coupon_rate: Decimal
    frequency: int
    maturity: date

    def __post_init__(self):
        if self.frequency not in (1, 2, 4):
            raise ValueError("frequency must be 1, 2 or 4")
