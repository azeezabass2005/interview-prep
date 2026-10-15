import os
import tempfile
from datetime import datetime

from oms.api.handlers import OmsApi
from oms.clock import FixedClock
from oms.db import Database
from oms.services.executions import ExecutionService
from oms.services.orders import OrderService
from oms.services.positions import PositionService

NOW = datetime(2026, 6, 1, 14, 30)


class TempDb:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "oms.db"))
        self.db.initialize()

    def cleanup(self):
        self._dir.cleanup()


def make_api(tmp):
    clock = FixedClock(NOW)
    return OmsApi(OrderService(tmp.db, clock), ExecutionService(tmp.db, clock), PositionService(tmp.db))


def order_body(qty=100, price="20.00", side="BUY", symbol="ABC", account="ACC1"):
    return {"account": account, "symbol": symbol, "side": side, "quantity": qty, "limit_price": price}


def exec_body(order_id, exec_id, qty, price):
    return {"exec_id": exec_id, "order_id": order_id, "quantity": qty, "price": price,
            "executed_at": NOW.isoformat()}
