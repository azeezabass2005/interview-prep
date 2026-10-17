import unittest
from decimal import Decimal

from robo.app import build_app
from robo.services.planner import quantity


def world(weights, cash, holdings=None, restricted=(), prices=None):
    api = build_app()
    api.model("M", weights)
    for symbol in set(weights) | set(holdings or {}):
        api.price(symbol, (prices or {}).get(symbol, "100"))
    api.open({"account_id": "A", "model": "M", "cash": cash, "holdings": holdings or {}, "restricted": list(restricted)})
    return api.plan("A")[1]["trades"]


class HiddenRobo(unittest.TestCase):
    def test_B1_cash_buffer(self):
        self.assertEqual(world({"AAA": 50, "BBB": 50}, "10000"), [["BUY", "AAA", 49], ["BUY", "BBB", 49]])

    def test_B2_band_on_total_value(self):
        trades = world({"CCC": 5, "DDD": 95}, "9300", {"CCC": 7})
        self.assertNotIn("CCC", [t[1] for t in trades])

    def test_B3_sells_before_buys(self):
        trades = world({"ZZZ": 40, "BBB": 60}, "2000", {"ZZZ": 100, "BBB": 10}, prices={"ZZZ": "50", "BBB": "300"})
        self.assertEqual(trades[0][0], "SELL")
        self.assertIn(["BUY", "BBB", 9], trades)

    def test_B4_round_toward_zero(self):
        self.assertEqual(quantity(Decimal("3920"), Decimal("5000"), Decimal("50")), -21)

    def test_B5_restricted_weight_redistributed(self):
        self.assertEqual(world({"AAA": 50, "BBB": 25, "CCC": 25}, "10000", restricted=["AAA"]),
                         [["BUY", "BBB", 49], ["BUY", "CCC", 49]])
