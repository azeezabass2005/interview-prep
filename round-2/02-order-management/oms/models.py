from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

NEW = "NEW"
PARTIALLY_FILLED = "PARTIALLY_FILLED"
FILLED = "FILLED"
CANCELLED = "CANCELLED"
FINAL_STATES = (FILLED, CANCELLED)


@dataclass
class Order:
    order_id: str
    account: str
    symbol: str
    side: str
    quantity: int
    limit_price: Decimal
    status: str
    filled_qty: int
    avg_price: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

    @property
    def remaining(self) -> int:
        return self.quantity - self.filled_qty


@dataclass(frozen=True)
class Execution:
    exec_id: str
    order_id: str
    quantity: int
    price: Decimal
    executed_at: datetime
