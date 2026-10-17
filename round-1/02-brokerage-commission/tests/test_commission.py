import unittest
from decimal import Decimal

from commission import FeeEngine


class TestCommission(unittest.TestCase):
    def test_small_buy_pays_minimum(self):
        engine = FeeEngine()
        trade = engine.book("t1", "acc", "EQUITY", "BUY", 100, "20.00", "2026-03-02")
        self.assertEqual(trade.commission, Decimal("1.00"))


if __name__ == "__main__":
    unittest.main()
