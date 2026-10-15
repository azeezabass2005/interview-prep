from ..audit import AuditLog
from ..db import Database
from ..errors import NotFound
from ..ids import new_order_id
from ..models import CANCELLED, NEW, Order
from ..repositories.orders import OrderRepository
from .validation import validate_order


class OrderService:
    def __init__(self, db: Database, clock):
        self._orders = OrderRepository(db)
        self._audit = AuditLog(db, clock)
        self._clock = clock

    def place_order(self, payload: dict) -> Order:
        data = validate_order(payload)
        now = self._clock.now()
        order = Order(new_order_id(), data["account"], data["symbol"], data["side"], data["quantity"],
                      data["limit_price"], NEW, 0, None, now, now)
        self._orders.insert(order)
        self._audit.record(order.order_id, "PLACED", quantity=order.quantity, price=order.limit_price)
        return order

    def get(self, order_id: str) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise NotFound(order_id)
        return order

    def cancel_order(self, order_id: str) -> Order:
        order = self.get(order_id)
        self._orders.set_status(order_id, CANCELLED, self._clock.now())
        self._audit.record(order_id, "CANCELLED", filled_qty=order.filled_qty)
        return self.get(order_id)
