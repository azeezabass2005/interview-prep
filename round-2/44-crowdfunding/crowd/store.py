import itertools
from typing import Dict, Optional

from .models import Campaign


class InMemoryStore:
    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self._ids = itertools.count(1)

    def next_id(self) -> int:
        return next(self._ids)

    def campaign(self, campaign_id: str) -> Optional[Campaign]:
        return self.campaigns.get(campaign_id)
