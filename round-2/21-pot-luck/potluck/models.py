from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple

OPEN, CLOSED, SETTLED = "OPEN", "CLOSED", "SETTLED"
ACTIVE, CANCELLED = "ACTIVE", "CANCELLED"


@dataclass(frozen=True)
class Participant:
    participant_id: str
    name: str
    email: str


@dataclass
class Entry:
    entry_id: int
    draw_id: int
    participant_id: str
    code: str
    status: str = ACTIVE
    created_at: Optional[datetime] = None


@dataclass
class Draw:
    draw_id: int
    number: int
    status: str
    carried_in_cents: int
    opened_at: datetime
    closed_at: Optional[datetime] = None
    winning_code: Optional[str] = None
    pot_cents: Optional[int] = None
    entry_ids: Tuple[int, ...] = ()


@dataclass(frozen=True)
class Payout:
    entry_id: int
    participant_id: str
    matches: int
    amount_cents: int


@dataclass(frozen=True)
class Settlement:
    draw_id: int
    payouts: Tuple[Payout, ...] = field(default_factory=tuple)
    awarded_cents: int = 0
    rollover_cents: int = 0

    def amount_for(self, entry_id: int) -> int:
        return sum(p.amount_cents for p in self.payouts if p.entry_id == entry_id)
