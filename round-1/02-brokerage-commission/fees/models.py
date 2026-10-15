from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class Trade:
    trade_id: str
    account: str
    side: str  # "BUY" or "SELL"
    notional: Decimal
    executed_at: datetime


@dataclass
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
    account: str
    lines: List[StatementLine] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return sum((line.total for line in self.lines), Decimal("0.00"))

    def line_for(self, trade_id: str) -> StatementLine:
        return next(line for line in self.lines if line.trade_id == trade_id)
