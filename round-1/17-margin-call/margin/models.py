from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

HAIRCUTS = {"EQUITY": Decimal("0.25"), "ETF": Decimal("0.15"), "BOND": Decimal("0.10")}
CONCENTRATION_LIMIT = Decimal("0.40")
CONCENTRATED_HAIRCUT = Decimal("0.50")
SHORT_REQUIREMENT = Decimal("0.30")
CALL_ROUNDING = Decimal("100")


@dataclass(frozen=True)
class Position:
    symbol: str
    asset_class: str
    quantity: int
    price: Decimal

    @property
    def market_value(self) -> Decimal:
        return self.quantity * self.price

    @property
    def is_long(self) -> bool:
        return self.quantity > 0


@dataclass
class Account:
    account_id: str
    cash: Decimal
    positions: List[Position] = field(default_factory=list)
