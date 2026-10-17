import unittest
from decimal import Decimal

from pnl import PnlService


class HiddenPnl(unittest.TestCase):
    def test_B1_oldest_lot_first(self):
        p = PnlService()
        p.buy("ABC", 10, "100")
        p.buy("ABC", 10, "120")
        self.assertEqual(p.sell("ABC", 10, "130"), Decimal("300.00"))

    def test_B2_sell_commission_reduces_proceeds(self):
        p = PnlService()
        p.buy("ABC", 10, "100")
        self.assertEqual(p.sell("ABC", 10, "110", commission="5"), Decimal("95.00"))

    def test_B3_split_keeps_total_cost(self):
        p = PnlService()
        p.buy("ABC", 10, "100")
        p.split("ABC", 2)
        self.assertEqual(p.unrealized("ABC", "55"), Decimal("100.00"))

    def test_B4_partial_lot_close(self):
        p = PnlService()
        p.buy("ABC", 10, "100")
        self.assertEqual(p.sell("ABC", 4, "110"), Decimal("40.00"))

    def test_B5_no_short_selling(self):
        p = PnlService()
        p.buy("ABC", 10, "100")
        with self.assertRaises(Exception):
            p.sell("ABC", 15, "110")
