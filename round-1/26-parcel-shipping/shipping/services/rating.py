from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable

from ..config import CARRIERS, OVERSIZE_FEE, OVERSIZE_INCHES, RESIDENTIAL_FEE
from ..errors import ShippingError
from ..models import Package
from .weights import billable_weight


def cents(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def package_rate(pkg: Package, carrier: str, zone: int, residential: bool) -> Decimal:
    table = CARRIERS[carrier]["zones"]
    if zone not in table:
        raise ShippingError(f"unknown zone {zone}")
    first, extra = table[zone]
    base = first + extra * (billable_weight(pkg, carrier) - 1)
    oversize = OVERSIZE_FEE if pkg.longest > OVERSIZE_INCHES else Decimal("0")
    residential_fee = RESIDENTIAL_FEE if residential else Decimal("0")
    fuel = cents((base + oversize + residential_fee) * CARRIERS[carrier]["fuel"])
    return base + oversize + fuel + residential_fee


def order_rate(packages: Iterable[Package], carrier: str, zone: int, residential: bool) -> Decimal:
    return sum((package_rate(p, carrier, zone, residential) for p in packages), Decimal("0.00"))
