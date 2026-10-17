from decimal import ROUND_CEILING, Decimal
from typing import Optional

from ..models import Client

TENTH = Decimal("0.1")


def refill(client: Client, now: Decimal) -> None:
    elapsed = Decimal(int(max(now - client.last_refill, Decimal(0))))
    client.tokens = client.tokens + elapsed * client.plan.refill_per_second
    client.last_refill = now


def wait_time(client: Client, cost: int) -> Optional[Decimal]:
    if cost > client.plan.capacity:
        return None
    missing = cost - client.tokens
    return (missing / client.plan.capacity).quantize(TENTH, rounding=ROUND_CEILING)
