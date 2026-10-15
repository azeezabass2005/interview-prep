from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Item:
    name: str
    price_cents: int
    sharers: Tuple[str, ...]

    def __post_init__(self):
        if not self.sharers:
            raise ValueError(f"item {self.name!r} has no sharers")
        if self.price_cents < 0:
            raise ValueError("negative price")


@dataclass
class Bill:
    items: List[Item]
    payer: str
    tip_percent: int = 18
    coupon_cents: int = 0


@dataclass
class Transfer:
    sender: str
    receiver: str
    amount_cents: int


@dataclass
class Breakdown:
    subtotals: Dict[str, int]
    subtotal: int
    coupon: int
    tax: int
    tip_percent: int
    tip: int
    total: int
    shares: Dict[str, int] = field(default_factory=dict)
