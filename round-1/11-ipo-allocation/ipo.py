from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

RETAIL_SHARE = Decimal("0.20")
RETAIL_LOT = 100
KINDS = ("RETAIL", "INSTITUTIONAL")


class IpoError(Exception):
    pass


@dataclass
class Order:
    order_id: str
    investor: str
    kind: str
    shares: int
    limit: Optional[Decimal]
    priority: int
    cancelled: bool = False


class OrderBook:
    def __init__(self, offering):
        self.offering = offering
        self.orders = {}
        self._clock = 0

    def _tick(self):
        self._clock += 1
        return self._clock

    def place(self, order_id, investor, kind, shares, limit=None):
        if order_id in self.orders or kind not in KINDS or shares <= 0:
            raise IpoError("bad order")
        limit = Decimal(str(limit)) if limit is not None else None
        self.orders[order_id] = Order(order_id, investor, kind, shares, limit, self._tick())

    def _live(self, order_id):
        order = self.orders.get(order_id)
        if order is None or order.cancelled:
            raise IpoError("no such live order")
        return order

    def amend(self, order_id, shares=None, limit=None):
        order = self._live(order_id)
        if shares is not None:
            if shares <= 0:
                raise IpoError("bad size")
            order.shares = shares
        if limit is not None:
            order.limit = Decimal(str(limit))

    def cancel(self, order_id):
        self._live(order_id).cancelled = True

    def _eligible(self, kind, price):
        return [o for o in self.orders.values() if o.kind == kind and (o.limit is None or o.limit > price)]

    @staticmethod
    def _pro_rata(orders, available, lot):
        demand = sum(o.shares for o in orders)
        if demand <= available:
            return {o.order_id: o.shares for o in orders}
        alloc = {o.order_id: (o.shares * available // demand) // lot * lot for o in orders}
        left = available - sum(alloc.values())
        ranked = sorted(orders, key=lambda o: (-o.shares, o.priority))
        while left >= lot:
            gave = False
            for o in ranked:
                if left >= lot and alloc[o.order_id] + lot <= o.shares:
                    alloc[o.order_id] += lot
                    left -= lot
                    gave = True
            if not gave:
                break
        return alloc

    def allocate(self, price):
        price = Decimal(str(price))
        retail = self._eligible("RETAIL", price)
        institutional = self._eligible("INSTITUTIONAL", price)
        retail_avail = int(self.offering * RETAIL_SHARE)
        inst_avail = self.offering - retail_avail
        result = self._pro_rata(retail, retail_avail, 1)
        result.update(self._pro_rata(institutional, inst_avail, 1))
        return result
