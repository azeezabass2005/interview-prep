import itertools
from dataclasses import dataclass
from typing import List

LOT_SIZE = 100


@dataclass(frozen=True)
class Order:
    investor: str
    shares: int
    seq: int


class BookClosed(Exception):
    pass


class OrderBook:
    def __init__(self, offering_shares: int):
        if offering_shares <= 0 or offering_shares % LOT_SIZE:
            raise ValueError("offering must be a positive number of whole lots")
        self.offering_shares = offering_shares
        self.orders: List[Order] = []
        self.closed = False
        self._seq = itertools.count(1)

    def submit(self, investor: str, shares: int) -> Order:
        if shares <= 0:
            raise ValueError("order must be positive")
        if any(o.investor == investor for o in self.orders):
            raise ValueError(f"{investor} already has an order")
        order = Order(investor, shares, next(self._seq))
        self.orders.append(order)
        return order

    def close(self) -> None:
        self.closed = True
