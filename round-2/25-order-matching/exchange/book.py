from collections import deque
from typing import Deque, Dict, List, Optional, Tuple

from .models import BUY, Order


class BookSide:
    def __init__(self, is_bid: bool):
        self.is_bid = is_bid
        self.levels: Dict[int, Deque[Order]] = {}

    def best_price(self) -> Optional[int]:
        if not self.levels:
            return None
        return max(self.levels) if self.is_bid else min(self.levels)

    def add(self, order: Order) -> None:
        self.levels.setdefault(order.price, deque()).append(order)

    def add_front(self, order: Order) -> None:
        self.levels.setdefault(order.price, deque()).appendleft(order)

    def remove(self, order: Order) -> None:
        self.levels[order.price].remove(order)

    def drop_level_if_empty(self, price: int) -> None:
        if price in self.levels and not self.levels[price]:
            del self.levels[price]

    def depth(self, n: int) -> List[Tuple[int, int]]:
        prices = sorted(self.levels, reverse=self.is_bid)[:n]
        return [(p, sum(o.remaining for o in self.levels[p])) for p in prices]


class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids = BookSide(is_bid=True)
        self.asks = BookSide(is_bid=False)

    def side_for(self, order: Order) -> BookSide:
        return self.bids if order.side == BUY else self.asks

    def opposite(self, order: Order) -> BookSide:
        return self.asks if order.side == BUY else self.bids
