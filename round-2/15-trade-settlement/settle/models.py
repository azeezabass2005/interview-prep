from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Tuple


@dataclass(frozen=True)
class Trade:
    trade_id: str
    account: str
    security: str
    asset_class: str
    side: str  # BUY / SELL
    quantity: int
    price: Decimal
    trade_date: date

    @property
    def signed_qty(self) -> int:
        return self.quantity if self.side == "BUY" else -self.quantity


@dataclass(frozen=True)
class Confirm:
    broker_ref: str
    trade_id: str
    side: str
    quantity: int
    price: str  # as received from the broker


@dataclass(frozen=True)
class Instruction:
    instruction_id: int
    account: str
    security: str
    settle_date: date
    net_quantity: int
    net_cash: Decimal
    trade_ids: Tuple[str, ...]
