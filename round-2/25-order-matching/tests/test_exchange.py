import unittest

from exchange.app import build_app


class TestExchange(unittest.TestCase):
    def test_simple_cross(self):
        api, _ = build_app()
        api.submit("m1", {"order_id": "S1", "symbol": "ABC", "side": "SELL", "price": 100, "quantity": 10})
        status, body = api.submit("m2", {"order_id": "B1", "symbol": "ABC", "side": "BUY", "price": 100, "quantity": 10})
        self.assertEqual(status, 201)
        self.assertEqual(body["status"], "FILLED")


if __name__ == "__main__":
    unittest.main()
