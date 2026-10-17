import unittest

from rebalance import Account, Rebalancer

HALF = {"AAA": "0.5", "BBB": "0.5"}


class HiddenRebalance(unittest.TestCase):
    def test_B1_exactly_five_points_is_inside_the_band(self):
        r = Rebalancer({"AAA": 100, "BBB": 100})
        self.assertEqual(r.plan(Account(0, {"AAA": 55, "BBB": 45}), HALF), [])

    def test_B2_two_percent_cash_buffer(self):
        r = Rebalancer({"AAA": 100, "BBB": 100})
        self.assertIn(("BBB", "BUY", 29), r.plan(Account(0, {"AAA": 80, "BBB": 20}), HALF))

    def test_B3_restricted_weight_redistributed(self):
        r = Rebalancer({"AAA": 100, "BBB": 100, "CCC": 100})
        account = Account(8000, {"CCC": 20}, {"CCC"})
        plan = r.plan(account, {"AAA": "0.5", "BBB": "0.25", "CCC": "0.25"})
        self.assertIn(("AAA", "BUY", 52), plan)

    def test_B4_sells_round_toward_zero(self):
        r = Rebalancer({"AAA": 30, "BBB": 100})
        self.assertIn(("AAA", "SELL", 136), r.plan(Account(0, {"AAA": 300, "BBB": 10}), HALF))

    def test_B5_sells_before_buys(self):
        r = Rebalancer({"AAA": 100, "BBB": 100})
        plan = r.plan(Account(0, {"AAA": 20, "BBB": 80}), HALF)
        self.assertEqual([side for _, side, _ in plan], ["SELL", "BUY"])
