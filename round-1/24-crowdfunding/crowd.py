from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Optional

PLATFORM_FEE = Decimal("0.05")
PROCESSING_PCT = Decimal("0.03")
PROCESSING_FIXED = Decimal("0.20")
CENT = Decimal("0.01")


def money(x):
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


class CrowdError(Exception):
    pass


@dataclass
class Tier:
    name: str
    minimum: Decimal
    slots: int
    taken: int = 0


@dataclass
class Pledge:
    backer: str
    amount: Decimal
    tier: Optional[str]


@dataclass
class Campaign:
    goal: Decimal
    deadline: datetime
    tiers: Dict[str, Tier] = field(default_factory=dict)
    pledges: Dict[str, Pledge] = field(default_factory=dict)
    settled: bool = False


class Platform:
    def __init__(self, gateway):
        self.gateway = gateway
        self.campaigns = {}

    def create(self, campaign_id, goal, deadline, tiers=()):
        c = Campaign(Decimal(str(goal)), deadline)
        for name, minimum, slots in tiers:
            c.tiers[name] = Tier(name, Decimal(str(minimum)), slots)
        self.campaigns[campaign_id] = c

    def _open(self, campaign_id, at):
        c = self.campaigns[campaign_id]
        if at > c.deadline:
            raise CrowdError("campaign closed")
        return c

    def _claim(self, c, tier_name, amount):
        if tier_name is None:
            return
        tier = c.tiers.get(tier_name)
        if tier is None or amount < tier.minimum or tier.taken >= tier.slots:
            raise CrowdError("tier unavailable")
        tier.taken += 1

    def pledge(self, campaign_id, backer, amount, at, tier=None):
        c = self._open(campaign_id, at)
        amount = Decimal(str(amount))
        if backer in c.pledges or amount <= 0:
            raise CrowdError("bad pledge")
        self._claim(c, tier, amount)
        c.pledges[backer] = Pledge(backer, amount, tier)

    def change(self, campaign_id, backer, amount, at, tier=None):
        c = self._open(campaign_id, at)
        old = c.pledges.get(backer)
        if old is None:
            raise CrowdError("no pledge to change")
        amount = Decimal(str(amount))
        if tier != old.tier:
            self._claim(c, tier, amount)
        c.pledges[backer] = Pledge(backer, amount, tier)

    def cancel(self, campaign_id, backer, at):
        c = self._open(campaign_id, at)
        if c.pledges.pop(backer, None) is None:
            raise CrowdError("no pledge to cancel")

    def total(self, campaign_id):
        return sum((p.amount for p in self.campaigns[campaign_id].pledges.values()), Decimal("0"))

    def settle(self, campaign_id, at):
        c = self.campaigns[campaign_id]
        if at <= c.deadline or c.settled:
            raise CrowdError("cannot settle now")
        c.settled = True
        if self.total(campaign_id) <= c.goal:
            return {"funded": False, "collected": Decimal("0.00"), "payout": Decimal("0.00"), "failed": []}
        collected, processing, failed = Decimal("0"), Decimal("0"), []
        for p in c.pledges.values():
            if self.gateway.charge(p.backer, p.amount):
                collected += p.amount
                processing += money(p.amount * PROCESSING_PCT)
            else:
                failed.append(p.backer)
        processing += PROCESSING_FIXED * len(c.pledges)
        platform = money(collected * PLATFORM_FEE)
        return {"funded": True, "collected": collected, "platform_fee": platform, "processing_fee": processing,
                "payout": collected - platform - processing, "failed": failed}
