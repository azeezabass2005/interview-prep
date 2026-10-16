from datetime import datetime
from decimal import Decimal

from ..errors import CrowdError
from ..models import Campaign, Tier
from ..store import InMemoryStore


class CampaignService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def create(self, campaign_id: str, goal, deadline: datetime, tiers) -> Campaign:
        goal = Decimal(str(goal))
        if goal <= 0 or not tiers:
            raise CrowdError("a campaign needs a positive goal and at least one tier")
        c = Campaign(campaign_id, goal, deadline,
                     {t["name"]: Tier(t["name"], Decimal(str(t["minimum"])), t.get("limit")) for t in tiers})
        self._store.campaigns[campaign_id] = c
        return c
