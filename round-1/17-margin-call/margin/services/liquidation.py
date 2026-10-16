from datetime import date
from decimal import Decimal
from typing import List, Tuple

from ..models import Account
from .valuation import Valuation


def liquidation_plan(valuation: Valuation, account: Account, run_date: date, amount: Decimal) -> List[Tuple[str, int]]:
    longs = [l for l in valuation.lines(account, run_date) if l.quantity > 0]
    longs.sort(key=lambda l: (-l.haircut, -l.market_value))
    plan, remaining = [], amount
    for line in longs:
        if remaining <= 0:
            break
        per_share = line.price * line.haircut
        shares = int(min(-(-remaining // per_share), line.quantity))
        plan.append((line.symbol, shares))
        remaining -= shares * per_share
    return plan
