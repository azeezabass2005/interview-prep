import unittest

from tests.helpers import TempDb, exec_body, make_api, order_body


class TestOrders(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDb()
        self.api = make_api(self.tmp)

    def tearDown(self):
        self.tmp.cleanup()

    def test_place_order(self):
        resp = self.api.post_order(order_body())
        self.assertEqual(resp.status, 201)
        self.assertEqual(resp.body["status"], "NEW")

    def test_invalid_quantity(self):
        self.assertEqual(self.api.post_order(order_body(qty=0)).status, 400)

    def test_invalid_tick(self):
        self.assertEqual(self.api.post_order(order_body(price="20.005")).status, 400)

    def test_cancel_new_order(self):
        order_id = self.api.post_order(order_body()).body["order_id"]
        self.assertEqual(self.api.delete_order(order_id).body["status"], "CANCELLED")

    def test_unknown_order(self):
        self.assertEqual(self.api.get_order("nope").status, 404)


class TestExecutions(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDb()
        self.api = make_api(self.tmp)
        self.order_id = self.api.post_order(order_body(qty=100)).body["order_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_fill(self):
        body = self.api.post_execution(exec_body(self.order_id, "E1", 100, "19.95")).body
        self.assertEqual(body["status"], "FILLED")
        self.assertEqual(body["avg_price"], "19.9500")

    def test_partial_fill(self):
        body = self.api.post_execution(exec_body(self.order_id, "E1", 40, "20.00")).body
        self.assertEqual((body["status"], body["filled_qty"]), ("PARTIALLY_FILLED", 40))

    def test_redelivered_execution_ignored(self):
        self.api.post_execution(exec_body(self.order_id, "E1", 40, "20.00"))
        body = self.api.post_execution(exec_body(self.order_id, "E1", 40, "20.00")).body
        self.assertEqual(body["filled_qty"], 40)

    def test_position_from_executions(self):
        self.api.post_execution(exec_body(self.order_id, "E1", 60, "20.00"))
        self.assertEqual(self.api.get_position("ACC1", "abc").body["position"], 60)


if __name__ == "__main__":
    unittest.main()
