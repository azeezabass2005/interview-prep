import unittest

from exchange.app import build_app


def order(api, oid, side, price, qty, member="m", type_="LIMIT"):
    return api.submit(member, {"order_id": oid, "symbol": "ABC", "side": side, "price": price, "quantity": qty, "type": type_})


class HiddenExchange(unittest.TestCase):
    def setUp(self):
        self.api, self.engine = build_app()

    def test_B1_partial_fill_keeps_priority(self):
        order(self.api, "S1", "SELL", 100, 100)
        order(self.api, "S2", "SELL", 100, 100)
        first = order(self.api, "B1", "BUY", 100, 30)[1]["trades"]
        second = order(self.api, "B2", "BUY", 100, 30)[1]["trades"]
        self.assertEqual([t["sell"] for t in first + second], ["S1", "S1"])

    def test_B2_trades_at_resting_price(self):
        order(self.api, "S1", "SELL", 101, 100)
        order(self.api, "S2", "SELL", 100, 50)
        order(self.api, "S3", "SELL", 100, 70)
        trades = order(self.api, "B1", "BUY", 101, 130)[1]["trades"]
        self.assertEqual([(t["sell"], t["price"], t["quantity"]) for t in trades],
                         [("S2", 100, 50), ("S3", 100, 70), ("S1", 101, 10)])

    def test_B3_ioc_never_rests(self):
        order(self.api, "S1", "SELL", 100, 100)
        body = order(self.api, "B1", "BUY", 100, 150, type_="IOC")[1]
        self.assertEqual(body["filled"], 100)
        self.assertEqual(self.api.depth("ABC")[1]["bids"], [])

    def test_B4_amend_down_keeps_priority(self):
        order(self.api, "S1", "SELL", 100, 100)
        order(self.api, "S2", "SELL", 100, 100)
        self.api.amend("S1", {"quantity": 60})
        trades = order(self.api, "B1", "BUY", 100, 10)[1]["trades"]
        self.assertEqual(trades[0]["sell"], "S1")

    def test_B5_cancel_clears_empty_level(self):
        order(self.api, "S1", "SELL", 101, 10)
        order(self.api, "S2", "SELL", 102, 10)
        self.api.cancel("S1")
        trades = order(self.api, "B1", "BUY", 102, 5)[1]["trades"]
        self.assertEqual(trades[0]["sell"], "S2")
