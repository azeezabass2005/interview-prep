from datetime import date

from ..config import TIER_THRESHOLDS
from ..store import InMemoryStore


class StatusService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def tier(self, member_id: str, on: date) -> str:
        miles = self._store.qualifying_miles(member_id, on.year)
        for name, threshold in TIER_THRESHOLDS:
            if miles >= threshold:
                return name
        return "BASE"
