from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Security:
    ticker: str
    shares: int
    free_float: Decimal  # fraction, e.g. Decimal("0.60")
    price: Decimal
