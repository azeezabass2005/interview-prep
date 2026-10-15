import unittest
from decimal import Decimal as D

from rebalance.engine import plan, target_values
from rebalance.models import Trade
from tests.helpers import portfolio, weights


class TestRebalance(unittest.TestCase):
    def test_total_value(self):
        p = portfolio(2000, ("AAA", 100, 50), ("BBB", 10, 300))
        self.assertEqual(p.total_value(), D("10000"))

    def test_weights_must_sum_to_one(self):
        with self.assertRaises(ValueError):
            target_values(portfolio(100), weights(AAA=0.5))

    def test_balanced_portfolio_needs_no_trades(self):
        p = portfolio(200, ("AAA", 98, 50), ("BBB", 98, 50))
        self.assertEqual(plan(p, weights(AAA=0.5, BBB=0.5)), [])

    def test_spec_example_as_listed(self):
        p = portfolio(2000, ("AAA", 100, 50), ("BBB", 10, 300))
        trades = plan(p, weights(AAA=0.4, BBB=0.6))
        self.assertEqual([t.side for t in trades], ["SELL", "BUY"])
        self.assertEqual(trades[0].symbol, "AAA")


if __name__ == "__main__":
    unittest.main()
