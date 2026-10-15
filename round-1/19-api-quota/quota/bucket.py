from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal
from typing import Optional

from .plans import Plan

TENTH = Decimal("0.1")


@dataclass(frozen=True)
class Decision:
    allowed: bool
    retry_after: Optional[Decimal] = None


class TokenBucket:
    def __init__(self, plan: Plan, now: Decimal):
        self.plan = plan
        self.tokens = plan.capacity
        self.last = now

    def _refill(self, now: Decimal) -> None:
        elapsed = Decimal(int(max(now - self.last, Decimal(0))))
        self.tokens = self.tokens + elapsed * self.plan.refill_per_second
        self.last = now

    def try_consume(self, cost: int, now: Decimal) -> Decision:
        self._refill(now)
        if self.tokens >= cost:
            self.tokens -= cost
            return Decision(True)
        missing = cost - self.tokens
        wait = (missing / self.plan.capacity).quantize(TENTH, rounding=ROUND_CEILING)
        return Decision(False, wait)

    def change_plan(self, plan: Plan, now: Decimal) -> None:
        self._refill(now)
        self.plan = plan
