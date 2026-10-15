from collections import defaultdict
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import Dict, Iterable

from .models import NightTips, Shift
from .policy import CARD_FEE_RATE, MIN_HOURS, ROLE_POINTS

CENT = Decimal("0.01")


def pool_amount(tips: NightTips) -> Decimal:
    gross = tips.card + tips.cash
    return (gross * (1 - CARD_FEE_RATE)).quantize(CENT, rounding=ROUND_HALF_UP)


def weights(shifts: Iterable[Shift]) -> Dict[str, Decimal]:
    hours = defaultdict(Decimal)
    weight = {}
    for shift in shifts:
        if shift.role not in ROLE_POINTS:
            raise ValueError(f"unknown role {shift.role}")
        hours[shift.employee] += shift.hours
        weight[shift.employee] = ROLE_POINTS[shift.role] * shift.hours
    return {name: w for name, w in weight.items() if hours[name] > MIN_HOURS}


def distribute(tips: NightTips, shifts: Iterable[Shift]) -> Dict[str, Decimal]:
    pool = pool_amount(tips)
    w = weights(shifts)
    total = sum(w.values(), Decimal(0))
    if total == 0:
        return {}
    exact = {name: pool * wt / total for name, wt in w.items()}
    shares = {name: amt.quantize(CENT, rounding=ROUND_DOWN) for name, amt in exact.items()}
    leftover_cents = int((pool - sum(shares.values())) / CENT)
    for name in sorted(shares)[:leftover_cents]:
        shares[name] += CENT
    return shares
