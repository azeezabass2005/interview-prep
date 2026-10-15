from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional

from .rates import (BASE_RATES, CITY_FEE_PER_NIGHT, LOS_LONG, LOS_SHORT, PROMOS, TAX_RATE,
                    WEEKEND_SURCHARGE)


def cents(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Quote:
    room: str
    check_in: date
    nightly: List[Decimal]
    los_discount: Decimal
    promo: Decimal
    room_total: Decimal
    tax: Decimal
    city_fee: Decimal
    total: Decimal


def nightly_rates(room: str, check_in: date, nights: int) -> List[Decimal]:
    rates = []
    for i in range(nights):
        night = check_in + timedelta(days=i)
        rate = BASE_RATES[room]
        if night.weekday() in (5, 6):
            rate = cents(rate * (1 + WEEKEND_SURCHARGE))
        rates.append(rate)
    return rates


def los_discount_rate(nights: int) -> Decimal:
    if nights > LOS_LONG[0]:
        return LOS_LONG[1]
    if nights >= LOS_SHORT[0]:
        return LOS_SHORT[1]
    return Decimal("0")


def quote(room: str, check_in: date, nights: int, promo_code: Optional[str] = None) -> Quote:
    if nights < 1:
        raise ValueError("stay must be at least one night")
    if room not in BASE_RATES:
        raise ValueError(f"unknown room type {room}")
    nightly = nightly_rates(room, check_in, nights)
    subtotal = sum(nightly, Decimal("0"))

    promo = PROMOS.get(promo_code, Decimal("0")) if promo_code else Decimal("0")
    after_promo = subtotal - promo
    los = cents(after_promo * los_discount_rate(nights))
    room_total = after_promo - los

    city_fee = CITY_FEE_PER_NIGHT * nights
    tax = cents((room_total + city_fee) * TAX_RATE)
    return Quote(room, check_in, nightly, los, promo, room_total, tax, city_fee, room_total + tax + city_fee)
