from dataclasses import dataclass
from typing import Optional

from .config import WINDOW_SECONDS
from .plans import PlanCache


@dataclass(frozen=True)
class Decision:
    allowed: bool
    limit: int
    remaining: int
    retry_after: Optional[int] = None


class RateLimiter:
    def __init__(self, counters, plans: PlanCache, clock):
        self._counters = counters
        self._plans = plans
        self._clock = clock

    def check(self, tenant_id: str, user_id: str) -> Decision:
        now = self._clock.time()
        window_start = int(now // WINDOW_SECONDS) * WINDOW_SECONDS
        limit = self._plans.limit_for(tenant_id)
        count = self._counters.increment(user_id, window_start)
        if count <= limit:
            return Decision(True, limit, limit - count)
        retry_after = max(1, int(now - window_start))
        return Decision(False, limit, 0, retry_after)
