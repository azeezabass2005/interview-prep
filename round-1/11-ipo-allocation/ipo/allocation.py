from typing import Dict, List

from .book import LOT_SIZE, Order, OrderBook


def _to_lots(shares: float) -> int:
    return int(round(shares / LOT_SIZE)) * LOT_SIZE


def allocate(book: OrderBook) -> Dict[str, int]:
    orders: List[Order] = list(book.orders)
    offering = book.offering_shares
    demand = sum(o.shares for o in orders)
    alloc = {o.investor: 0 for o in orders}

    if demand <= offering:
        return {o.investor: o.shares for o in orders}

    remaining = offering

    # 1. guarantee one lot each, in arrival order
    for order in sorted(orders, key=lambda o: o.shares, reverse=True):
        if remaining < LOT_SIZE:
            break
        alloc[order.investor] += LOT_SIZE
        remaining -= LOT_SIZE

    # 2. pro-rata on remaining demand
    unfilled = {o.investor: o.shares - alloc[o.investor] for o in orders}
    total_unfilled = sum(unfilled.values())
    pool = remaining
    if total_unfilled:
        for order in orders:
            share = _to_lots(pool * unfilled[order.investor] / total_unfilled)
            alloc[order.investor] += share
            remaining -= share

    # 3. leftover lots to the largest unfilled demand, earliest order on ties
    while remaining >= LOT_SIZE:
        candidates = [o for o in orders if o.shares - alloc[o.investor] > 0]
        if not candidates:
            break
        pick = max(candidates, key=lambda o: (o.shares - alloc[o.investor], o.seq))
        alloc[pick.investor] += LOT_SIZE
        remaining -= LOT_SIZE

    return alloc
