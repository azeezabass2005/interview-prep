from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

ACTIVE, CANCELLED, CHARGED, FAILED = "ACTIVE", "CANCELLED", "CHARGED", "FAILED"


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
    status: str = ACTIVE


@dataclass
class Campaign:
    campaign_id: str
    goal: Decimal
    deadline: datetime
    tiers: Dict[str, Tier]
    pledges: Dict[int, Pledge] = field(default_factory=dict)
    settled: bool = False
    result: Optional[dict] = None
