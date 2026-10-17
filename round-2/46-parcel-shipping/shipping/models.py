from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Package:
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal

    @property
    def longest(self) -> Decimal:
        return max(self.length, self.width, self.height)
