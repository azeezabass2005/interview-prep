from dataclasses import dataclass, field
from typing import List, Optional

INCREMENT_CENTS = 500
OPENING_PRICE_CENTS = 1000
BUYERS_PREMIUM_PERCENT = 10


@dataclass(frozen=True)
class Bid:
    bidder: str
    amount_cents: int
    seq: int  # global submission order


@dataclass
class Lot:
    lot_id: str
    reserve_cents: Optional[int] = None
    bids: List[Bid] = field(default_factory=list)
    closed: bool = False


@dataclass(frozen=True)
class Result:
    lot_id: str
    winner: str
    hammer_cents: int
    invoice_cents: int


class AuctionError(Exception):
    pass
