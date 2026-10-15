from datetime import date
from decimal import Decimal
from typing import Dict

from .models import Breakdown

DAILY_REGULAR = Decimal(8)
DAILY_DOUBLE_AFTER = Decimal(12)
WEEKLY_REGULAR = Decimal(40)
ZERO = Decimal(0)


def classify(day_hours: Dict[date, Decimal]) -> Breakdown:
    """Split a week's hours into regular, 1.5x and 2x buckets."""
    regular = overtime = double = ZERO
    for day, hours in sorted(day_hours.items()):
        regular += min(hours, DAILY_REGULAR)
        overtime += max(hours - DAILY_REGULAR, ZERO)
        double += max(hours - DAILY_DOUBLE_AFTER, ZERO)

    total = sum(day_hours.values(), ZERO)
    weekly_overtime = max(total - WEEKLY_REGULAR, ZERO)
    regular -= weekly_overtime
    overtime += weekly_overtime
    return Breakdown(regular, overtime, double)
