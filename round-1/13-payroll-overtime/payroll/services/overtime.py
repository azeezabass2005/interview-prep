from decimal import Decimal
from typing import List, Tuple

from ..models import DayHours

DAILY_REGULAR = Decimal(8)
DAILY_DOUBLE_AFTER = Decimal(12)
WEEKLY_REGULAR = Decimal(40)
ZERO = Decimal(0)


def split_day(hours: Decimal) -> Tuple[Decimal, Decimal, Decimal]:
    regular = min(hours, DAILY_REGULAR)
    overtime = max(hours - DAILY_REGULAR, ZERO)
    double = max(hours - DAILY_DOUBLE_AFTER, ZERO)
    return regular, overtime, double


def classify(days: List[DayHours]) -> List[Tuple[DayHours, Decimal, Decimal, Decimal]]:
    rows = [[d, *split_day(d.hours)] for d in days]
    total_hours = sum((d.hours for d in days), ZERO)
    excess = max(total_hours - WEEKLY_REGULAR, ZERO)
    for row in reversed(rows):
        if excess <= 0:
            break
        moved = min(row[1], excess)
        row[1] -= moved
        row[2] += moved
        excess -= moved
    return [tuple(r) for r in rows]
