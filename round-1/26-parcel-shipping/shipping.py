import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

CARRIERS = {
    "SWIFT": {"base": Decimal("8.00"), "per_kg": {1: Decimal("2.00"), 2: Decimal("3.00")}, "oversize": Decimal("15.00"), "days": {1: 1, 2: 2}},
    "BUDGET": {"base": Decimal("5.00"), "per_kg": {1: Decimal("1.50"), 2: Decimal("2.50")}, "oversize": Decimal("20.00"), "days": {1: 3, 2: 5}},
}
DIM_DIVISOR = Decimal("5000")
OVERSIZE_CM = 120
FUEL = Decimal("0.10")
RESIDENTIAL = Decimal("3.00")
CUTOFF = time(15, 0)
FREE_THRESHOLD = Decimal("100")
CENT = Decimal("0.01")


class ShippingError(Exception):
    pass


@dataclass(frozen=True)
class Parcel:
    kg: Decimal
    length: int
    width: int
    height: int


def billable_weight(p):
    dimensional = Decimal(p.length * p.width * p.height) / DIM_DIVISOR
    weight = max(Decimal(str(p.kg)), dimensional)
    return Decimal(round(weight * 2)) / 2


def price(carrier, parcel, zone, residential=False):
    c = CARRIERS[carrier]
    charge = c["base"] + c["per_kg"][zone] * billable_weight(parcel)
    if max(parcel.length, parcel.width, parcel.height) > OVERSIZE_CM:
        charge += c["oversize"]
    if residential:
        charge += RESIDENTIAL
    charge += charge * FUEL
    return charge.quantize(CENT, rounding=ROUND_HALF_UP)


def _next_business_day(d):
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def ship_date(placed_at):
    d = placed_at.date()
    if placed_at.time() >= CUTOFF or d.weekday() >= 5:
        d = _next_business_day(d)
    return d


def delivery_date(carrier, zone, placed_at):
    return ship_date(placed_at) + timedelta(days=CARRIERS[carrier]["days"][zone])


def choose(parcel, zone, order_total, placed_at, deadline: Optional[date] = None, residential=False):
    if zone not in (1, 2):
        raise ShippingError("unknown zone")
    if Decimal(str(order_total)) >= FREE_THRESHOLD:
        return {"carrier": "BUDGET", "price": Decimal("0.00"), "delivery": delivery_date("BUDGET", zone, placed_at)}
    options = []
    for carrier in ("SWIFT", "BUDGET"):
        when = delivery_date(carrier, zone, placed_at)
        if deadline is None or when <= deadline:
            options.append({"carrier": carrier, "price": price(carrier, parcel, zone, residential), "delivery": when})
    if not options:
        raise ShippingError("no carrier meets the deadline")
    return min(options, key=lambda o: o["price"])
