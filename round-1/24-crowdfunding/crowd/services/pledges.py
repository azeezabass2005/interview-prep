from decimal import Decimal, InvalidOperation

from ..errors import CrowdError, NotFound, Rejected
from ..models import ACTIVE, CANCELLED, Campaign, Pledge
from ..store import InMemoryStore


class PledgeService:
    def __init__(self, store: InMemoryStore, clock):
        self._store = store
        self._clock = clock

    def _open(self, campaign_id: str) -> Campaign:
        c = self._store.campaign(campaign_id)
        if c is None:
            raise NotFound(campaign_id)
        if c.settled or self._clock.now() >= c.deadline:
            raise Rejected("campaign has ended")
        return c

    def claimed(self, c: Campaign, tier: str) -> int:
        return sum(1 for p in c.pledges.values() if p.tier == tier and p.status == ACTIVE)

    def _validate(self, c: Campaign, tier: str, amount) -> Decimal:
        if tier not in c.tiers:
            raise CrowdError(f"unknown tier {tier}")
        try:
            amount = Decimal(str(amount))
        except InvalidOperation:
            raise CrowdError("amount must be a number")
        if amount < c.tiers[tier].minimum:
            raise CrowdError(f"{tier} requires at least {c.tiers[tier].minimum}")
        return amount

    def pledge(self, campaign_id: str, backer: str, tier: str, amount) -> Pledge:
        c = self._open(campaign_id)
        amount = self._validate(c, tier, amount)
        limit = c.tiers[tier].limit
        if limit is not None and self.claimed(c, tier) > limit:
            raise Rejected(f"{tier} is sold out")
        p = Pledge(self._store.next_id(), backer, tier, amount)
        c.pledges[p.pledge_id] = p
        return p

    def change(self, campaign_id: str, pledge_id: int, tier: str, amount) -> Pledge:
        c = self._open(campaign_id)
        p = c.pledges.get(pledge_id)
        if p is None or p.status != ACTIVE:
            raise NotFound(f"pledge {pledge_id}")
        p.amount = self._validate(c, tier, amount)
        p.tier = tier
        return p

    def cancel(self, campaign_id: str, pledge_id: int) -> Pledge:
        c = self._open(campaign_id)
        p = c.pledges.get(pledge_id)
        if p is None or p.status != ACTIVE:
            raise NotFound(f"pledge {pledge_id}")
        p.status = CANCELLED
        return p
