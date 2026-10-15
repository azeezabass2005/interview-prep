from typing import List

from .book import OrderBook
from .models import BUY, Fill, Order


def _crosses(incoming: Order, price: int) -> bool:
    return price <= incoming.price if incoming.side == BUY else price >= incoming.price


class MatchingEngine:
    def __init__(self):
        self.book = OrderBook()

    def submit(self, incoming: Order) -> List[Fill]:
        fills: List[Fill] = []
        opposite = self.book.opposite_of(incoming)

        while incoming.remaining > 0:
            best = opposite.best_price()
            if best is None or not _crosses(incoming, best):
                break
            level = opposite.level(best)
            resting = level.popleft()
            qty = min(incoming.remaining, resting.remaining)
            fills.append(Fill(incoming.order_id, resting.order_id, incoming.price, qty))
            incoming.remaining -= qty
            resting.remaining -= qty
            if resting.remaining > 0:
                level.append(resting)
            else:
                del self.book.resting[resting.order_id]
            if not level:
                opposite.remove_level(best)

        if not fills:
            self.book.rest(incoming)
        return fills

    def cancel(self, order_id: str) -> bool:
        order = self.book.resting.pop(order_id, None)
        if order is None:
            return False
        self.book.side_for(order).cancel(order)
        return True
