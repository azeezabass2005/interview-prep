from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional

from .models import (BUYERS_PREMIUM_PERCENT, INCREMENT_CENTS, OPENING_PRICE_CENTS, Bid, Lot, Result)


def effective_bids(lot: Lot) -> List[Bid]:
    """One bid per bidder."""
    best = {}
    for bid in lot.bids:
        current = best.get(bid.bidder)
        if current is None or bid.amount_cents > current.amount_cents:
            best[bid.bidder] = bid
    return list(best.values())


def rank(bids: List[Bid]) -> List[Bid]:
    """Highest first; ties go to the earlier bid."""
    return sorted(bids, key=lambda b: (b.amount_cents, b.seq), reverse=True)


def invoice_for(amount_cents: int) -> int:
    total = Decimal(amount_cents) * (100 + BUYERS_PREMIUM_PERCENT) / 100
    return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def settle(lot: Lot) -> Optional[Result]:
    ranked = rank(effective_bids(lot))
    if not ranked:
        return None
    winner = ranked[0]
    if lot.reserve_cents is not None and winner.amount_cents < lot.reserve_cents:
        return None

    runner_up = ranked[1].amount_cents if len(ranked) > 1 else 0
    hammer = runner_up + INCREMENT_CENTS
    return Result(lot.lot_id, winner.bidder, hammer, invoice_for(winner.amount_cents))
