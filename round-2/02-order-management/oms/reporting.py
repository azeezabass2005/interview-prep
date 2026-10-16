from collections import defaultdict
from decimal import Decimal

from .repositories.orders import OrderRepository


def blotter(orders: OrderRepository, account: str) -> dict:
    notional = defaultdict(Decimal)
    counts = defaultdict(int)
    for o in orders.for_account(account):
        counts[o.status] += 1
        if o.avg_price is not None:
            sign = 1 if o.side == "BUY" else -1
            notional[o.symbol] += sign * o.filled_qty * o.avg_price
    return {"account": account, "notional": dict(notional), "counts": dict(counts)}
