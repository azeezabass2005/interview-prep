from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List


@dataclass
class Member:
    member_id: str
    plan: str
    credits: int = 0
    fees: Decimal = Decimal("0.00")

    @property
    def premium(self) -> bool:
        return self.plan == "PREMIUM"


@dataclass
class StudioClass:
    class_id: str
    starts_at: datetime
    capacity: int
    booked: List[str] = field(default_factory=list)
    waitlist: List[str] = field(default_factory=list)
