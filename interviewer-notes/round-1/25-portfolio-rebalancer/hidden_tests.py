import unittest
from decimal import Decimal as D

from rebalance.engine import plan, target_values, trade_quantity
from rebalance.models import Trade
from tests.helpers import portfolio, weights


class HiddenRebalance(unittest.TestCase):
    def test_B1_targets_exclude_cash_buffer(self):
        p = portfolio(2000, ("AAA", 100, 50), ("BBB", 10, 300))
        self.assertEqual(target_values(p, weights(AAA=0.4, BBB=0.6)), {"AAA": D("3920.000"), "BBB": D("5880.000")})

    def test_B2_band_is_share_of_total_value(self):
        p = portfolio(9300, ("CCC", 7, 100), ("DDD", 0, 100))
        trades = plan(p, weights(CCC=0.05, DDD=0.95))
        self.assertNotIn("CCC", [t.symbol for t in trades])

    def test_B3_sells_before_buys(self):
        p = portfolio(2000, ("BBB", 10, 300), ("AAA", 100, 50))
        trades = plan(p, weights(BBB=0.6, AAA=0.4))
        self.assertEqual(trades, [Trade("SELL", "AAA", 21), Trade("BUY", "BBB", 9)])

    def test_B4_quantities_round_toward_zero(self):
        self.assertEqual(trade_quantity(D("3920"), D("5000"), D("50")), -21)

    def test_B5_largest_underweight_bought_first(self):
        p = portfolio(1200, ("WWW", 44, 100), ("XXX", 24, 100), ("YYY", 20, 100))
        trades = plan(p, weights(WWW=0.4, XXX=0.3, YYY=0.3))
        self.assertEqual(trades, [Trade("BUY", "YYY", 9), Trade("BUY", "XXX", 1)])
