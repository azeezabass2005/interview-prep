from dataclasses import dataclass, field
from typing import List


@dataclass
class Entry:
    entry_id: int
    participant: str
    code: str


@dataclass
class Draw:
    draw_number: int
    winning_code: str
    pot_cents: int
    entries: List[Entry]


@dataclass
class Payout:
    entry_id: int
    participant: str
    matches: int
    amount_cents: int


@dataclass
class PayoutPlan:
    draw_number: int
    payouts: List[Payout] = field(default_factory=list)
    total_awarded_cents: int = 0
    rollover_cents: int = 0

    def amount_for(self, entry_id):
        return sum(p.amount_cents for p in self.payouts if p.entry_id == entry_id)
