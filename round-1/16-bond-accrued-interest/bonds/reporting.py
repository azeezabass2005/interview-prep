from collections import defaultdict
from decimal import Decimal

from .store import InMemoryStore


def settlement_ladder(store: InMemoryStore) -> dict:
    ladder = defaultdict(lambda: Decimal("0.00"))
    for t in store.trades:
        sign = -1 if t.side == "BUY" else 1
        ladder[t.settle_date.isoformat()] += sign * t.settlement_amount
    return {d: str(v) for d, v in sorted(ladder.items())}
