from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from ..config import (BASE, BOOKING_FEE, FREE_WAIT_MINUTES, MINIMUM, PER_MILE, PER_MINUTE, PROMO_MAX, PROMOS,
                      WAIT_PER_MINUTE)
from ..models import FareBreakdown

CENT = Decimal("0.01")


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def started_minutes(start: datetime, end: datetime) -> int:
    seconds = (end - start).total_seconds()
    return int(seconds // 60)


def metered(miles: Decimal, ride_minutes: int) -> Decimal:
    return cents(BASE + miles.quantize(CENT, rounding=ROUND_HALF_UP) * PER_MILE + ride_minutes * PER_MINUTE)


def wait_charge(wait_minutes: int) -> Decimal:
    if wait_minutes <= FREE_WAIT_MINUTES:
        return Decimal("0.00")
    return cents(wait_minutes * WAIT_PER_MINUTE)


def compute_fare(miles: Decimal, ride_minutes: int, wait_minutes: int, surge: Decimal, tolls: Decimal,
                 promo: Optional[str]) -> FareBreakdown:
    base_fare = metered(miles, ride_minutes)
    surged = cents(base_fare * surge)
    wait = wait_charge(wait_minutes)
    subtotal = max(cents(surged + wait + BOOKING_FEE), MINIMUM)
    discount = Decimal("0.00")
    if promo:
        discount = min(cents((subtotal + tolls) * PROMOS[promo]), PROMO_MAX)
    total = subtotal - discount + tolls
    return FareBreakdown(base_fare, surged, wait, subtotal, discount, tolls, total)
