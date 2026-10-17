from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

MAX_QTY = 1_000_000
MAX_NOTIONAL = Decimal("1000000")
SUB_DOLLAR_TICK = Decimal("0.0001")
TICK = Decimal("0.01")
PRICE_PLACES = Decimal("0.0001")


class OmsError(Exception):
    pass


@dataclass
class Order:
    order_id: str
    account: str
    symbol: str
    side: str
    quantity: int
    price: Decimal
    status: str = "NEW"
    filled: int = 0
    notional_filled: Decimal = Decimal("0")
    fill_prices: tuple = ()
    reason: str = ""

    @property
    def avg_price(self):
        if not self.filled:
            return None
        return (sum(self.fill_prices) / len(self.fill_prices)).quantize(PRICE_PLACES, rounding=ROUND_HALF_UP)


class OrderManager:
    def __init__(self):
        self.orders = {}
        self.exec_ids = set()
        self.positions = {}

    @staticmethod
    def _tick(price):
        return SUB_DOLLAR_TICK if price < 1 else TICK

    def submit(self, order_id, account, symbol, side, quantity, price):
        if order_id in self.orders or side not in ("BUY", "SELL"):
            raise OmsError("bad order")
        price = Decimal(str(price))
        order = Order(order_id, account, symbol, side, quantity, price)
        if not 1 <= quantity < MAX_QTY:
            order.status, order.reason = "REJECTED", "bad quantity"
        elif price <= 0 or price % self._tick(price) != 0:
            order.status, order.reason = "REJECTED", "price not on tick"
        elif quantity * price > MAX_NOTIONAL:
            order.status, order.reason = "REJECTED", "notional too large"
        self.orders[order_id] = order
        return order

    def execute(self, exec_id, order_id, quantity, price):
        order = self.orders.get(order_id)
        if order is None or order.status in ("CANCELLED", "REJECTED", "FILLED"):
            raise OmsError("order cannot be filled")
        if quantity <= 0 or order.filled + quantity > order.quantity:
            raise OmsError("overfill")
        price = Decimal(str(price))
        self.exec_ids.add(exec_id)
        order.filled += quantity
        order.notional_filled += quantity * price
        order.fill_prices += (price,)
        if order.filled == order.quantity:
            order.status = "FILLED"
        key = (order.account, order.symbol)
        self.positions[key] = self.positions.get(key, 0) + quantity
        return order

    def cancel(self, order_id):
        order = self.orders.get(order_id)
        if order is None or order.status not in ("NEW", "PARTIALLY_FILLED"):
            raise OmsError("cannot cancel")
        order.status = "CANCELLED"
        return order

    def position(self, account, symbol):
        return self.positions.get((account, symbol), 0)
