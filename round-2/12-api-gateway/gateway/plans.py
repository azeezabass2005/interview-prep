from typing import Dict, Tuple

from .config import PLAN_CACHE_TTL_SECONDS, PLAN_LIMITS
from .repositories.tenants import TenantRepository


class PlanCache:
    def __init__(self, tenants: TenantRepository, clock, ttl_seconds: int = PLAN_CACHE_TTL_SECONDS):
        self._tenants = tenants
        self._clock = clock
        self._ttl = ttl_seconds
        self._cache: Dict[str, Tuple[str, float]] = {}

    def limit_for(self, tenant_id: str) -> int:
        cached = self._cache.get(tenant_id)
        if cached is None:
            plan = self._tenants.plan_for(tenant_id) or "free"
            self._cache[tenant_id] = (plan, self._clock.time())
            cached = self._cache[tenant_id]
        return PLAN_LIMITS[cached[0]]
