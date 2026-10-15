from .auth import Authenticator
from .counters import LocalCounterStore
from .limiter import RateLimiter
from .plans import PlanCache
from .proxy import Gateway
from .repositories.keys import ApiKeyRepository
from .repositories.tenants import TenantRepository
from .upstream import FakeUpstream


def build_gateway(db, clock, upstream=None) -> Gateway:
    """One gateway instance. Production starts several of these behind a load balancer."""
    counters = LocalCounterStore()
    plans = PlanCache(TenantRepository(db), clock)
    return Gateway(Authenticator(ApiKeyRepository(db)), RateLimiter(counters, plans, clock), upstream or FakeUpstream())
