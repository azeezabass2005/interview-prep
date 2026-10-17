import unittest
from decimal import Decimal

from commission import FeeEngine


class HiddenCommission(unittest.TestCase):
    def test_B1_cap_beats_minimum(self):
        trade = FeeEngine().book("t1", "acc", "EQUITY", "BUY", 10, "5.00", "2026-03-02")
        self.assertEqual(trade.commission, Decimal("0.50"))

    def test_B2_order_crossing_band_is_split(self):
        e = FeeEngine()
        e.book("t1", "acc", "EQUITY", "BUY", 299_000, "50", "2026-03-02")
        self.assertEqual(e.book("t2", "acc", "EQUITY", "BUY", 2_000, "50", "2026-03-03").commission, Decimal("8.00"))

    def test_B3_reg_fee_rounds_up(self):
        trade = FeeEngine().book("t1", "acc", "EQUITY", "SELL", 150, "10.00", "2026-03-02")
        self.assertEqual(trade.reg_fee, Decimal("0.05"))

    def test_B4_busted_trades_do_not_count_toward_volume(self):
        e = FeeEngine()
        e.book("t1", "acc", "EQUITY", "BUY", 350_000, "100", "2026-03-02")
        e.bust("t1")
        self.assertEqual(e.book("t2", "acc", "EQUITY", "BUY", 1_000, "100", "2026-03-03").commission, Decimal("5.00"))

    def test_B5_volume_is_per_account(self):
        e = FeeEngine()
        e.book("t1", "big", "EQUITY", "BUY", 300_000, "100", "2026-03-02")
        self.assertEqual(e.book("t2", "small", "EQUITY", "BUY", 1_000, "100", "2026-03-03").commission, Decimal("5.00"))
