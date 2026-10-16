from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional

from ..config import (CITY_FEE, LOS_TIERS, NON_REFUNDABLE_DISCOUNT, PROMOS, ROOM_TYPES, TAX_RATE,
                      WEEKEND_SURCHARGE)
from ..errors import HotelError
from ..models import NON_REFUNDABLE, Quote


def cents(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def nights(check_in: date, check_out: date) -> List[date]:
    return [check_in + timedelta(days=i) for i in range((check_out - check_in).days)]


def nightly_rates(room_type: str, check_in: date, check_out: date) -> List[Decimal]:
    base = ROOM_TYPES[room_type][1]
    return [cents(base * (1 + WEEKEND_SURCHARGE)) if n.weekday() in (5, 6) else base for n in nights(check_in, check_out)]


def los_rate(count: int) -> Decimal:
    for minimum, rate in LOS_TIERS:
        if count >= minimum:
            return rate
    return Decimal("0")


def price(room_type: str, check_in: date, check_out: date, plan: str, promo: Optional[str]) -> Quote:
    if room_type not in ROOM_TYPES:
        raise HotelError(f"unknown room type {room_type}")
    if check_out <= check_in:
        raise HotelError("check-out must be after check-in")
    if promo is not None and promo not in PROMOS:
        raise HotelError(f"unknown promo {promo}")
    rates = nightly_rates(room_type, check_in, check_out)
    subtotal = sum(rates, Decimal("0"))
    promo_amount = PROMOS[promo] if promo else Decimal("0")
    after_promo = subtotal - promo_amount
    los = cents(after_promo * los_rate(len(rates)))
    plan_discount = cents((after_promo - los) * NON_REFUNDABLE_DISCOUNT) if plan == NON_REFUNDABLE else Decimal("0")
    room_total = max(after_promo - los - plan_discount, Decimal("0"))
    city_fee = CITY_FEE * len(rates)
    tax = cents((room_total + city_fee) * TAX_RATE)
    return Quote(tuple(rates), subtotal, los, plan_discount, promo_amount, room_total, tax, city_fee,
                 room_total + tax + city_fee)
