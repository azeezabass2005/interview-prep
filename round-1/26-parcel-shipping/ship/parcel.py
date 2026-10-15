import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .rates import DIM_DIVISOR


@dataclass(frozen=True)
class Package:
    length: Decimal
    width: Decimal
    height: Decimal
    weight_lb: Decimal

    @property
    def longest_side(self) -> Decimal:
        return max(self.length, self.width, self.height)


def dimensional_weight(pkg: Package) -> Decimal:
    return pkg.length * pkg.width * pkg.height / DIM_DIVISOR


def billable_weight(pkg: Package) -> int:
    heavier = max(pkg.weight_lb, dimensional_weight(pkg))
    return int(heavier.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
