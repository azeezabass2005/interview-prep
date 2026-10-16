from datetime import date
from typing import List, Tuple

from .calendar import shift_months
from .models import Bond


def coupon_dates(bond: Bond, back_to: date) -> List[date]:
    step = 12 // bond.frequency
    dates, n = [bond.maturity], 1
    while dates[-1] > back_to:
        dates.append(shift_months(bond.maturity, -step * n))
        n += 1
    return sorted(dates)


def surrounding_coupons(bond: Bond, settle: date) -> Tuple[date, date]:
    dates = coupon_dates(bond, settle)
    previous = max(d for d in dates if d < settle)
    following = min(d for d in dates if d > previous)
    return previous, following
