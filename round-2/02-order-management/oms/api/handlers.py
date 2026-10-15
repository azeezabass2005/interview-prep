from dataclasses import dataclass, field

from ..errors import OmsError
from ..models import Order
from ..services.executions import ExecutionService
from ..services.orders import OrderService
from ..services.positions import PositionService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


def order_json(o: Order) -> dict:
    return {"order_id": o.order_id, "account": o.account, "symbol": o.symbol, "side": o.side,
            "quantity": o.quantity, "limit_price": str(o.limit_price), "status": o.status,
            "filled_qty": o.filled_qty, "avg_price": str(o.avg_price) if o.avg_price is not None else None}


class OmsApi:
    def __init__(self, orders: OrderService, executions: ExecutionService, positions: PositionService):
        self._orders = orders
        self._executions = executions
        self._positions = positions

    def _call(self, fn, *args, status=200):
        try:
            return Response(status, order_json(fn(*args)))
        except OmsError as e:
            return Response(e.status, {"error": str(e)})

    def post_order(self, body: dict) -> Response:
        return self._call(self._orders.place_order, body, status=201)

    def get_order(self, order_id: str) -> Response:
        return self._call(self._orders.get, order_id)

    def delete_order(self, order_id: str) -> Response:
        return self._call(self._orders.cancel_order, order_id)

    def post_execution(self, body: dict) -> Response:
        return self._call(self._executions.apply_execution, body)

    def get_position(self, account: str, symbol: str) -> Response:
        return Response(200, {"account": account, "symbol": symbol.upper(),
                              "position": self._positions.position(account, symbol)})
