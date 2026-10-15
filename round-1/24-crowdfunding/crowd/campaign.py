import itertools
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Iterable, List

from .models import Outcome, Pledge, PledgeRejected, Tier

PLATFORM_RATE = Decimal("0.05")
PROCESSING_RATE = Decimal("0.03")
PER_PLEDGE_FEE = Decimal("0.20")
ZERO = Decimal("0.00")


def cents(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Campaign:
    def __init__(self, goal, deadline: datetime, tiers: Iterable[Tier], clock):
        self.goal = Decimal(goal)
        self.deadline = deadline
        self.tiers: Dict[str, Tier] = {t.name: t for t in tiers}
        self.pledges: List[Pledge] = []
        self._clock = clock
        self._ids = itertools.count(1)

    def _claimed(self, tier: str) -> int:
        return sum(1 for p in self.pledges if p.tier == tier and not p.cancelled)

    def pledge(self, backer: str, tier: str, amount) -> Pledge:
        amount = Decimal(amount)
        if tier not in self.tiers:
            raise PledgeRejected(f"unknown tier {tier}")
        t = self.tiers[tier]
        if amount < t.minimum:
            raise PledgeRejected(f"{tier} requires at least {t.minimum}")
        if t.limit is not None and self._claimed(tier) > t.limit:
            raise PledgeRejected(f"{tier} is sold out")
        p = Pledge(next(self._ids), backer, tier, amount)
        self.pledges.append(p)
        return p

    def cancel(self, pledge_id: int) -> None:
        for p in self.pledges:
            if p.pledge_id == pledge_id:
                p.cancelled = True
                return
        raise KeyError(pledge_id)

    def total(self) -> Decimal:
        return sum((p.amount for p in self.pledges), ZERO)

    def close(self) -> Outcome:
        total = self.total()
        funded = total > self.goal
        active = [p for p in self.pledges if not p.cancelled]
        platform = cents(total * PLATFORM_RATE)
        processing = cents((total - platform) * PROCESSING_RATE + PER_PLEDGE_FEE * len(active))
        payout = total - platform - processing if funded else ZERO
        return Outcome(funded, total, platform, processing, payout, active if funded else [])
