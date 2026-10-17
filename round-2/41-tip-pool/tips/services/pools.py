from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Iterable

from ..config import CARD_FEE_RATE, MIN_HOURS, ROLE_POINTS
from ..errors import TipsError
from ..models import Declaration, Shift
from .periods import hours_in_service


def pool_amount(declaration: Declaration) -> Decimal:
    gross = declaration.card + declaration.cash
    return (gross * (1 - CARD_FEE_RATE)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def weights(shifts: Iterable[Shift], day: date, service: str) -> Dict[str, Decimal]:
    hours = defaultdict(Decimal)
    weight: Dict[str, Decimal] = {}
    for shift in shifts:
        if shift.role not in ROLE_POINTS:
            raise TipsError(f"unknown role {shift.role}")
        h = hours_in_service(shift, day, service)
        if h == 0:
            continue
        hours[shift.employee] += h
        weight[shift.employee] = ROLE_POINTS[shift.role] * h
    return {name: w for name, w in weight.items() if hours[name] > MIN_HOURS}
