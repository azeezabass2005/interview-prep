from datetime import date
from decimal import Decimal

from .models import ACT_360, THIRTY_360


def days_30_360(start: date, end: date) -> int:
    d1, d2 = start.day, end.day
    if d1 == 31:
        d1 = 30
    if d2 == 31:
        d2 = 30
    return 360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)


def year_fraction(convention: str, start: date, end: date) -> Decimal:
    if convention == THIRTY_360:
        return Decimal(days_30_360(start, end)) / 360
    if convention == ACT_360:
        return Decimal((end - start).days) / 365
    raise ValueError(f"unsupported day count {convention}")
