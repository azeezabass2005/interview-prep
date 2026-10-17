from collections import deque
from typing import Deque, Dict, List, Optional, Tuple

from .models import BUY, Order


class BookSide:
    def __init__(self, is_bid: bool):
        # Initialize the price levels for either the bid or ask side.
        self.is_bid = is_bid
        self.levels: Dict[int, Deque[Order]] = {}

    def best_price(self) -> Optional[int]:
        # Return the highest bid or lowest ask price, or None if no levels exist.
        if not self.levels:
            return None
        return max(self.levels) if self.is_bid else min(self.levels)

    def add(self, order: Order) -> None:
        # Append an order to the back of its price-level queue.
        self.levels.setdefault(order.price, deque()).append(order)

    def add_front(self, order: Order) -> None:
        # Place an order at the front of its price-level queue.
        self.levels.setdefault(order.price, deque()).appendleft(order)

    def remove(self, order: Order) -> None:
        # Remove an order from its price-level queue.
        self.levels[order.price].remove(order)

    def drop_level_if_empty(self, price: int) -> None:
        # Delete a price level when it contains no orders.
        if price in self.levels and not self.levels[price]:
            del self.levels[price]

    def depth(self, n: int) -> List[Tuple[int, int]]:
        # Return prices and total remaining quantities for the best n levels.
        prices = sorted(self.levels, reverse=self.is_bid)[:n]
        return [(p, sum(o.remaining for o in self.levels[p])) for p in prices]


class OrderBook:
    def __init__(self, symbol: str):
        # Create separate bid and ask sides for a symbol.
        self.symbol = symbol
        self.bids = BookSide(is_bid=True)
        self.asks = BookSide(is_bid=False)

    def side_for(self, order: Order) -> BookSide:
        # Return the book side on which the order would rest.
        return self.bids if order.side == BUY else self.asks

    def opposite(self, order: Order) -> BookSide:
        # Return the opposing book side against which the order can match.
        return self.asks if order.side == BUY else self.bids
