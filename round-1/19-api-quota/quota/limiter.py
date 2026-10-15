from decimal import Decimal
from typing import Dict

from .bucket import Decision, TokenBucket
from .plans import ENDPOINT_COST, PLANS


class RateLimiter:
    def __init__(self, clock):
        self._clock = clock
        self._buckets: Dict[str, TokenBucket] = {}

    def register(self, client_id: str, plan_name: str) -> None:
        self._buckets[client_id] = TokenBucket(PLANS[plan_name], self._clock.now())

    def change_plan(self, client_id: str, plan_name: str) -> None:
        self._buckets[client_id].change_plan(PLANS[plan_name], self._clock.now())

    def check(self, client_id: str, endpoint: str) -> Decision:
        if endpoint not in ENDPOINT_COST:
            raise ValueError(f"unknown endpoint {endpoint}")
        return self._buckets[client_id].try_consume(ENDPOINT_COST[endpoint], self._clock.now())
