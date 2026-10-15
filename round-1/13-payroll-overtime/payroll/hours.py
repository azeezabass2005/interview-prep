from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict, Iterable

from .models import Shift


def hours_by_day(shifts: Iterable[Shift]) -> Dict[date, Decimal]:
    totals: Dict[date, Decimal] = defaultdict(Decimal)
    for shift in shifts:
        hours = Decimal(int((shift.end - shift.start).total_seconds() // 3600))
        totals[shift.end.date()] += hours
    return dict(totals)
