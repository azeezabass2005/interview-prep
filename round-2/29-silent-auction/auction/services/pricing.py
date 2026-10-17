from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from ..config import INCREMENTS
from ..models import Bid, Lot


def increment_for(amount: Decimal) -> Decimal:
    for upper, step in INCREMENTS:
        if upper is None or amount < upper:
            return step
    raise AssertionError("increment table must end unbounded")


def leading_bids(bids: List[Bid]) -> List[Bid]:
    best: Dict[int, Bid] = {}
    for bid in bids:
        current = best.get(bid.paddle)
        if current is None or bid.maximum > current.maximum:
            best[bid.paddle] = bid
    return sorted(best.values(), key=lambda b: (b.maximum, b.seq), reverse=True)


def standing(lot: Lot, bids: List[Bid]) -> Tuple[Optional[int], Decimal]:
    ranked = leading_bids(bids)
    if not ranked:
        return None, lot.opening
    winner = ranked[0]
    if len(ranked) == 1:
        return winner.paddle, lot.opening
    runner_up = ranked[1].maximum
    price = min(runner_up + increment_for(winner.maximum), winner.maximum)
    return winner.paddle, max(price, lot.opening)
