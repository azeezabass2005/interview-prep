from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List

EQUITY, OPTION = "EQUITY", "OPTION"
BUY, SELL = "BUY", "SELL"
ACTIVE, BUSTED = "ACTIVE", "BUSTED"


@dataclass(frozen=True)
class Account:
    account_id: str
    owner: str


@dataclass
class Trade:
    trade_id: str
    account_id: str
    asset_class: str
    side: str
    quantity: int
    price: Decimal
    executed_at: datetime
    status: str = ACTIVE


@dataclass(frozen=True)
class StatementLine:
    trade_id: str
    commission: Decimal
    discount: Decimal
    reg_fee: Decimal

    @property
    def total(self) -> Decimal:
        return self.commission - self.discount + self.reg_fee


@dataclass
class Statement:
    account_id: str
    year: int
    month: int
    lines: List[StatementLine] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return sum((line.total for line in self.lines), Decimal("0.00"))

    def line(self, trade_id: str) -> StatementLine:
        return next(l for l in self.lines if l.trade_id == trade_id)
