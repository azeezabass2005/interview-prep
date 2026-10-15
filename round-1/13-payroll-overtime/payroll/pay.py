from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable

from .hours import hours_by_day
from .models import Shift
from .overtime import classify


def weekly_pay(rate: Decimal, shifts: Iterable[Shift]) -> Decimal:
    b = classify(hours_by_day(shifts))
    gross = b.regular * rate + b.overtime * rate * Decimal("1.5") + b.double * rate * 2
    return gross.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
