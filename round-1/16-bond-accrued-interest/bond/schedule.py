from datetime import date
from typing import List, Tuple

from .calendar import add_months
from .models import Bond


def coupon_dates(bond: Bond, back_to: date) -> List[date]:
    """All coupon dates from maturity backwards to (and including) the first one on or before back_to."""
    step = 12 // bond.frequency
    dates = [bond.maturity]
    n = 1
    while dates[-1] > back_to:
        dates.append(add_months(bond.maturity, -step * n))
        n += 1
    return sorted(dates)


def previous_and_next(bond: Bond, settle: date) -> Tuple[date, date]:
    dates = coupon_dates(bond, settle)
    previous = max(d for d in dates if d < settle)
    following = min(d for d in dates if d > previous)
    return previous, following
