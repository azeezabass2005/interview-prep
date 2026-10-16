from typing import Dict, List

from ..config import LOT_SIZE
from ..models import Order


def to_lots(shares: float) -> int:
    return int(round(shares / LOT_SIZE)) * LOT_SIZE


def allocate_tranche(orders: List[Order], available: int, guarantee_lot: bool) -> Dict[str, int]:
    orders = sorted(orders, key=lambda o: o.seq)
    alloc = {o.investor: 0 for o in orders}
    demand = sum(o.shares for o in orders)
    if demand <= available:
        return {o.investor: o.shares for o in orders}
    remaining = available
    if guarantee_lot:
        for order in orders:
            if remaining < LOT_SIZE:
                break
            alloc[order.investor] += LOT_SIZE
            remaining -= LOT_SIZE
    unfilled = {o.investor: o.shares - alloc[o.investor] for o in orders}
    total_unfilled = sum(unfilled.values())
    pool = remaining
    if total_unfilled:
        for order in orders:
            share = min(to_lots(pool * unfilled[order.investor] / total_unfilled), unfilled[order.investor])
            alloc[order.investor] += share
            remaining -= share
    while remaining >= LOT_SIZE:
        candidates = [o for o in orders if o.shares > alloc[o.investor]]
        if not candidates:
            break
        pick = max(candidates, key=lambda o: (o.shares - alloc[o.investor], o.seq))
        alloc[pick.investor] += LOT_SIZE
        remaining -= LOT_SIZE
    return alloc
