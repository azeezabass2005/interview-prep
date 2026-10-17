from collections import deque
from dataclasses import dataclass
from decimal import Decimal

SIDES = ("BUY", "SELL")
TIFS = ("GTC", "IOC")
TICK = Decimal("0.01")


class OrderError(Exception):
    pass


@dataclass
class Order:
    order_id: str
    trader: str
    side: str
    price: Decimal
    quantity: int
    tif: str = "GTC"
    remaining: int = 0
    status: str = "NEW"


class OrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}
        self.orders = {}
        self.trades = []

    def _levels(self, side):
        return self.bids if side == "BUY" else self.asks

    def _validate(self, order_id, side, price, quantity, tif):
        if order_id in self.orders:
            raise OrderError("duplicate order id")
        if side not in SIDES or tif not in TIFS:
            raise OrderError("bad side or time in force")
        if quantity <= 0 or price <= 0 or price % TICK != 0:
            raise OrderError("bad price or quantity")

    def submit(self, order_id, trader, side, price, quantity, tif="GTC"):
        price = Decimal(str(price))
        self._validate(order_id, side, price, quantity, tif)
        order = Order(order_id, trader, side, price, quantity, tif, remaining=quantity)
        self.orders[order_id] = order
        self._match(order)
        if order.remaining:
            if order.tif == "IOC" and order.remaining == order.quantity:
                order.status = "CANCELLED"
            else:
                self._rest(order)
        return order

    def _crosses(self, order, price):
        return price < order.price if order.side == "BUY" else price > order.price

    def _match(self, order):
        opposite = self.asks if order.side == "BUY" else self.bids
        while order.remaining and opposite:
            best = min(opposite) if order.side == "BUY" else max(opposite)
            if not self._crosses(order, best):
                break
            queue = opposite[best]
            resting = queue[0]
            qty = min(order.remaining, resting.remaining)
            buy, sell = (order, resting) if order.side == "BUY" else (resting, order)
            self.trades.append({"buy_id": buy.order_id, "sell_id": sell.order_id, "price": order.price, "quantity": qty})
            for o in (order, resting):
                o.remaining -= qty
                o.status = "FILLED" if o.remaining == 0 else "PARTIAL"
            if resting.remaining == 0:
                queue.popleft()
                if not queue:
                    del opposite[best]

    def _rest(self, order):
        self._levels(order.side).setdefault(order.price, deque()).appendleft(order)

    def cancel(self, order_id):
        order = self.orders.get(order_id)
        if order is None or order.status not in ("NEW", "PARTIAL"):
            raise OrderError("order is not live")
        levels = self._levels(order.side)
        queue = levels[order.price]
        queue.remove(order)
        if not queue:
            del levels[order.price]
        order.status = "CANCELLED"
        return order

    def depth(self, side, n=5):
        levels = self._levels(side)
        prices = sorted(levels, reverse=(side == "BUY"))[:n]
        return [(p, sum(o.remaining for o in levels[p])) for p in prices]
