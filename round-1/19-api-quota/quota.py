from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class Plan:
    name: str
    capacity: int
    refill_per_second: int
    monthly_units: int
    hard_limit: bool
    base_price: Decimal
    overage_price: Decimal


PLANS = {
    "FREE": Plan("FREE", 10, 5, 1_000, True, Decimal("0.00"), Decimal("0")),
    "PRO": Plan("PRO", 50, 20, 100_000, False, Decimal("49.00"), Decimal("0.002")),
}
CENT = Decimal("0.01")


class QuotaError(Exception):
    pass


@dataclass
class Bucket:
    tokens: float
    updated: datetime


class Meter:
    def __init__(self):
        self.keys = {}
        self.buckets = {}
        self.usage = {}

    def create_key(self, key, plan, at):
        if plan not in PLANS:
            raise QuotaError("unknown plan")
        self.keys[key] = PLANS[plan]
        self.buckets[key] = Bucket(PLANS[plan].capacity, at)

    def monthly_usage(self, key, month):
        return self.usage.get(key, 0)

    def _refill(self, key, at):
        plan, bucket = self.keys[key], self.buckets[key]
        elapsed = (at - bucket.updated).total_seconds()
        if elapsed > 0:
            bucket.tokens = bucket.tokens + elapsed * plan.refill_per_second
            bucket.updated = at
        return bucket

    def request(self, key, at, cost=1):
        if key not in self.keys:
            return 403
        if cost < 1:
            raise QuotaError("cost must be at least 1")
        plan = self.keys[key]
        month = at.strftime("%Y-%m")
        used = self.monthly_usage(key, month)
        if plan.hard_limit and used > plan.monthly_units:
            return 429
        bucket = self._refill(key, at)
        bucket.tokens -= cost
        if bucket.tokens < 0:
            return 429
        self.usage[key] = used + cost
        return 200

    def invoice(self, key, month):
        plan = self.keys[key]
        used = self.monthly_usage(key, month)
        overage = used if used > plan.monthly_units else 0
        return (plan.base_price + overage * plan.overage_price).quantize(CENT, rounding=ROUND_HALF_UP)
