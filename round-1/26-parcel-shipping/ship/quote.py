from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable

from .parcel import Package, billable_weight
from .rates import (FREE_SHIPPING_THRESHOLD, FUEL_RATE, OVERSIZE_FEE, OVERSIZE_LENGTH,
                    RESIDENTIAL_FEE, ZONE_RATES)


def cents(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def package_cost(pkg: Package, zone: int, residential: bool) -> Decimal:
    if zone not in ZONE_RATES:
        raise ValueError(f"unknown zone {zone}")
    first, additional = ZONE_RATES[zone]
    weight = max(billable_weight(pkg), 1)
    base = first + additional * (weight - 1)
    oversize = OVERSIZE_FEE if pkg.longest_side >= OVERSIZE_LENGTH else Decimal("0")
    residential_fee = RESIDENTIAL_FEE if residential else Decimal("0")
    fuel = cents((base + oversize + residential_fee) * FUEL_RATE)
    return base + oversize + fuel + residential_fee


def order_shipping(packages: Iterable[Package], zone: int, residential: bool,
                   subtotal: Decimal, discount: Decimal = Decimal("0")) -> Decimal:
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal("0.00")
    return sum((package_cost(p, zone, residential) for p in packages), Decimal("0.00"))
