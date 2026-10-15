from decimal import Decimal
from typing import List, Tuple

from .calc import haircuts
from .models import Account


def liquidation_plan(account: Account, call: Decimal) -> List[Tuple[str, int]]:
    """Whole shares to sell, in order, to cover `call`."""
    cuts = haircuts(account)
    longs = [p for p in account.positions if p.is_long]
    longs.sort(key=lambda p: (cuts[p.symbol], p.market_value))

    plan = []
    remaining = call
    for p in longs:
        if remaining <= 0:
            break
        per_share = p.price * cuts[p.symbol]
        needed = -(-remaining // per_share)  # ceil
        shares = int(min(needed, p.quantity))
        plan.append((p.symbol, shares))
        remaining -= shares * per_share
    return plan
