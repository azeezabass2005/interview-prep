import threading
import unittest
from unittest import mock

from oms.clock import FixedClock
from oms.repositories.orders import OrderRepository
from oms.services.executions import ExecutionService
from tests.helpers import NOW, TempDb, exec_body, make_api, order_body


class HiddenOms(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDb()
        self.api = make_api(self.tmp)

    def tearDown(self):
        self.tmp.cleanup()

    def test_OMS201_quantity_weighted_average(self):
        oid = self.api.post_order(order_body(qty=400, price="10.50")).body["order_id"]
        self.api.post_execution(exec_body(oid, "E1", 100, "10.00"))
        body = self.api.post_execution(exec_body(oid, "E2", 300, "10.40")).body
        self.assertEqual(body["avg_price"], "10.3000")

    def test_OMS202_concurrent_executions_are_not_lost(self):
        oid = self.api.post_order(order_body(qty=100)).body["order_id"]
        a, b = ExecutionService(self.tmp.db, FixedClock(NOW)), ExecutionService(self.tmp.db, FixedClock(NOW))
        barrier = threading.Barrier(2, timeout=3)
        original = OrderRepository.get
        calls = {"n": 0}
        lock = threading.Lock()

        def paused_get(repo, order_id):
            result = original(repo, order_id)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        errors = []

        def run(svc, exec_id, price):
            try:
                svc.apply_execution(exec_body(oid, exec_id, 50, price))
            except Exception as e:
                errors.append(e)

        with mock.patch.object(OrderRepository, "get", paused_get):
            threads = [threading.Thread(target=run, args=(a, "E1", "20.00")),
                       threading.Thread(target=run, args=(b, "E2", "19.90"))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(errors, [])
        body = self.api.get_order(oid).body
        self.assertEqual((body["filled_qty"], body["status"], body["avg_price"]), (100, "FILLED", "19.9500"))

    def test_OMS203_cannot_cancel_filled_order_and_positions_stay_true(self):
        oid = self.api.post_order(order_body(qty=100)).body["order_id"]
        self.api.post_execution(exec_body(oid, "E1", 100, "20.00"))
        self.assertEqual(self.api.delete_order(oid).status, 409)
        self.assertEqual(self.api.get_order(oid).body["status"], "FILLED")
        partial = self.api.post_order(order_body(qty=100)).body["order_id"]
        self.api.post_execution(exec_body(partial, "E2", 40, "20.00"))
        self.assertEqual(self.api.delete_order(partial).body["status"], "CANCELLED")
        self.assertEqual(self.api.get_position("ACC1", "ABC").body["position"], 140)

    def test_OMS204_valid_ticks_accepted(self):
        for price in ("4.35", "1.15", "0.57", "0.0123"):
            self.assertEqual(self.api.post_order(order_body(price=price)).status, 201, price)
        for price in ("4.355", "0.00005"):
            self.assertEqual(self.api.post_order(order_body(price=price)).status, 400, price)
