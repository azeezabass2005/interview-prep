from decimal import Decimal

from ..errors import MeteringError, NotFound
from ..models import Client, Decision
from ..plans import COSTS, PLANS
from ..store import InMemoryStore
from . import meter
from .bucket import refill, wait_time


class Limiter:
    def __init__(self, store: InMemoryStore, clock):
        self._store = store
        self._clock = clock

    def register(self, client_id: str, plan: str) -> Client:
        if plan not in PLANS:
            raise MeteringError(f"unknown plan {plan}")
        p = PLANS[plan]
        client = Client(client_id, p, p.capacity, self._clock.time())
        self._store.clients[client_id] = client
        return client

    def change_plan(self, client_id: str, plan: str) -> Client:
        client = self._get(client_id)
        refill(client, self._clock.time())
        client.plan = PLANS[plan]
        client.tokens = min(client.tokens, client.plan.capacity)
        return client

    def _get(self, client_id: str) -> Client:
        client = self._store.client(client_id)
        if client is None:
            raise NotFound(client_id)
        return client

    def check(self, client_id: str, endpoint: str) -> Decision:
        if endpoint not in COSTS:
            raise MeteringError(f"unknown endpoint {endpoint}")
        client = self._get(client_id)
        cost = COSTS[endpoint]
        now = self._clock.time()
        refill(client, now)
        month = meter.month_key(now)
        if client.plan.hard_cap and meter.usage(client, month) + cost > client.plan.allowance:
            return Decision(False, None, "monthly allowance exhausted")
        meter.record(client, cost, now)
        if client.tokens >= cost:
            client.tokens -= cost
            return Decision(True)
        return Decision(False, wait_time(client, cost), "rate limited")
