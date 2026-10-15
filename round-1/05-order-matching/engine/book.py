from collections import deque
from typing import Deque, Dict, Optional

from .models import BUY, Order


class BookSide:
    """One side of the book: price -> FIFO queue of resting orders."""

    def __init__(self, is_bid: bool):
        self._is_bid = is_bid
        self._levels: Dict[int, Deque[Order]] = {}

    def best_price(self) -> Optional[int]:
        if not self._levels:
            return None
        return max(self._levels) if self._is_bid else min(self._levels)

    def add(self, order: Order) -> None:
        self._levels.setdefault(order.price, deque()).appendleft(order)

    def level(self, price: int) -> Deque[Order]:
        return self._levels[price]

    def remove_level(self, price: int) -> None:
        del self._levels[price]

    def cancel(self, order: Order) -> None:
        self._levels[order.price].remove(order)

    def depth(self) -> Dict[int, int]:
        return {price: sum(o.remaining for o in level) for price, level in self._levels.items()}


class OrderBook:
    def __init__(self):
        self.bids = BookSide(is_bid=True)
        self.asks = BookSide(is_bid=False)
        self.resting: Dict[str, Order] = {}

    def side_for(self, order: Order) -> BookSide:
        return self.bids if order.side == BUY else self.asks

    def opposite_of(self, order: Order) -> BookSide:
        return self.asks if order.side == BUY else self.bids

    def rest(self, order: Order) -> None:
        self.side_for(order).add(order)
        self.resting[order.order_id] = order
