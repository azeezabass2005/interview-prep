from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from ..audit import AuditLog
from ..db import Database
from ..errors import NotFound, ValidationError
from ..models import FILLED, PARTIALLY_FILLED, Execution, Order
from ..repositories.executions import ExecutionRepository
from ..repositories.orders import OrderRepository

PRICE_PLACES = Decimal("0.0001")


class ExecutionService:

    def __init__(self, db: Database, clock):
        self._orders = OrderRepository(db)
        self._executions = ExecutionRepository(db)
        self._audit = AuditLog(db, clock)
        self._clock = clock

    def apply_execution(self, report: dict) -> Order:
        execution = Execution(report["exec_id"], report["order_id"], int(report["quantity"]),
                              Decimal(str(report["price"])), datetime.fromisoformat(report["executed_at"]))
        if execution.quantity <= 0:
            raise ValidationError("execution quantity must be positive")

        order = self._orders.get(execution.order_id)
        if order is None:
            raise NotFound(execution.order_id)

        if not self._executions.insert_if_new(execution):
            return order

        filled = order.filled_qty + execution.quantity
        if order.avg_price is None:
            avg = execution.price
        else:
            avg = (order.avg_price + execution.price) / 2
        avg = avg.quantize(PRICE_PLACES, rounding=ROUND_HALF_UP)
        status = FILLED if filled >= order.quantity else PARTIALLY_FILLED

        self._orders.save_fill_state(order.order_id, filled, avg, status, self._clock.now())
        self._audit.record(order.order_id, "EXECUTION", exec_id=execution.exec_id, qty=execution.quantity)
        return self._orders.get(order.order_id)
