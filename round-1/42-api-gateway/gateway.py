from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

PLAN_LIMITS = {"FREE": 60, "PRO": 600}
FAILURE_THRESHOLD = 5
OPEN_FOR = timedelta(seconds=30)


class GatewayError(Exception):
    pass


@dataclass
class Route:
    prefix: str
    backend: str
    cost: int


@dataclass
class Breaker:
    failures: int = 0
    opened_at: Optional[datetime] = None


class Gateway:
    def __init__(self, clock):
        self.clock = clock
        self.routes = []
        self.backends = {}
        self.breakers = {}
        self.keys = {}
        self.blocked = set()
        self.usage = {}

    def add_backend(self, name, handler):
        self.backends[name] = handler
        self.breakers[name] = Breaker()

    def add_route(self, prefix, backend, cost=1):
        if backend not in self.backends:
            raise GatewayError("unknown backend")
        self.routes.append(Route(prefix, backend, cost))

    def add_key(self, key, plan):
        self.keys[key] = plan

    def block(self, ip):
        self.blocked.add(ip)

    def _route(self, path):
        for route in self.routes:
            if path.startswith(route.prefix):
                return route
        return None

    def _window(self, now):
        return now.replace(second=0, microsecond=0)

    def handle(self, key, ip, path):
        now = self.clock.now()
        if key not in self.keys:
            return 401, {}
        if ip in self.blocked:
            return 403, {}
        route = self._route(path)
        if route is None:
            return 404, {}
        window = self._window(now)
        used = self.usage.get((key, window), 0)
        if used + 1 > PLAN_LIMITS[self.keys[key]]:
            retry = int((now - window).total_seconds())
            return 429, {"Retry-After": str(retry)}
        self.usage[(key, window)] = used + 1
        breaker = self.breakers[route.backend]
        if breaker.opened_at is not None:
            if now - breaker.opened_at < OPEN_FOR:
                return 503, {}
            breaker.opened_at = None
        status = self.backends[route.backend](path)
        if status >= 500:
            breaker.failures += 1
            if breaker.failures >= FAILURE_THRESHOLD:
                breaker.opened_at = now
                breaker.failures = 0
        return status, {}
