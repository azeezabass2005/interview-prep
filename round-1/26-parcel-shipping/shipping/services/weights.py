from decimal import ROUND_HALF_UP, Decimal

from ..config import CARRIERS
from ..models import Package


def dimensional_weight(pkg: Package, carrier: str) -> Decimal:
    return pkg.length * pkg.width * pkg.height / CARRIERS[carrier]["divisor"]


def billable_weight(pkg: Package, carrier: str) -> int:
    heavier = max(pkg.weight, dimensional_weight(pkg, carrier))
    return max(1, int(heavier.quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
