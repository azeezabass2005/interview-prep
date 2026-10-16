from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass
class Lot:
    lot_id: str
    title: str
    opening: Decimal
    fmv: Decimal
    closes_at: datetime
    reserve: Optional[Decimal] = None
    closed: bool = False
    winner: Optional[str] = None
    hammer: Optional[Decimal] = None


@dataclass(frozen=True)
class Bidder:
    paddle: int
    name: str


@dataclass(frozen=True)
class Bid:
    lot_id: str
    paddle: int
    maximum: Decimal
    placed_at: datetime
    seq: int


@dataclass
class InvoiceLine:
    lot_id: str
    hammer: Decimal
    premium: Decimal
    deductible: Decimal


@dataclass
class Invoice:
    paddle: int
    lines: List[InvoiceLine] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return sum((l.hammer + l.premium for l in self.lines), Decimal("0.00"))
