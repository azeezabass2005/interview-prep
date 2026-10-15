from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict


@dataclass(frozen=True)
class Holding:
    symbol: str
    shares: int
    price: Decimal

    @property
    def value(self) -> Decimal:
        return self.shares * self.price


@dataclass
class Portfolio:
    cash: Decimal
    holdings: Dict[str, Holding] = field(default_factory=dict)

    def total_value(self) -> Decimal:
        return self.cash + sum((h.value for h in self.holdings.values()), Decimal(0))


@dataclass(frozen=True)
class Trade:
    side: str
    symbol: str
    shares: int
