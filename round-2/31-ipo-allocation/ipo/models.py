from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Optional

OPEN, CLOSED = "OPEN", "CLOSED"
ACTIVE, CANCELLED = "ACTIVE", "CANCELLED"
RETAIL, INSTITUTIONAL = "RETAIL", "INSTITUTIONAL"


@dataclass
class Order:
    investor: str
    shares: int
    limit: Decimal
    seq: int
    status: str = ACTIVE

    @property
    def category(self) -> str:
        from .config import RETAIL_MAX_SHARES
        return RETAIL if self.shares <= RETAIL_MAX_SHARES else INSTITUTIONAL


@dataclass
class Offering:
    offering_id: str
    shares: int
    status: str = OPEN
    final_price: Optional[Decimal] = None
    orders: Dict[str, Order] = field(default_factory=dict)
    allocations: Dict[str, int] = field(default_factory=dict)
