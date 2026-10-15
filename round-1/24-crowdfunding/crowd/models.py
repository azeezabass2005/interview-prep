from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class Tier:
    name: str
    minimum: Decimal
    limit: Optional[int] = None


@dataclass
class Pledge:
    pledge_id: int
    backer: str
    tier: str
    amount: Decimal
    cancelled: bool = False


@dataclass(frozen=True)
class Outcome:
    funded: bool
    total: Decimal
    platform_fee: Decimal
    processing_fee: Decimal
    payout: Decimal
    charged: List[Pledge] = field(default_factory=list)


class PledgeRejected(Exception):
    pass
