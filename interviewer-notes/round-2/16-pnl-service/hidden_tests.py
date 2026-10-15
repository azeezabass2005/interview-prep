import unittest

from tests.helpers import D, World


class HiddenPnl(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_PNL1601_fifo_realized(self):
        self.w.buy(100, "10", D(3, 2))
        self.w.buy(100, "20", D(3, 3))
        self.w.sell(100, "25", D(3, 4))
        self.w.prices.add("IBM", D(3, 4), "25")
        self.assertEqual(self.w.api.get_positions("GEQ", "2026-03-04").body["IBM"]["realized"], "1500.00")

    def test_PNL1602_latest_price_not_after_as_of(self):
        for d, px in ((D(2, 10), "150"), (D(3, 5), "180"), (D(3, 20), "190")):
            self.w.prices.add("IBM", d, px)
        self.w.buy(10, "170", D(3, 2))
        self.assertEqual(self.w.api.get_positions("GEQ", "2026-03-06").body["IBM"]["unrealized"], "100.00")

    def test_PNL1603_split_adjusts_only_earlier_lots(self):
        self.w.buy(100, "400", D(3, 3), security="XYZ")
        self.w.splits.add("XYZ", D(3, 10), "4")
        self.w.buy(50, "101", D(3, 12), security="XYZ")
        self.w.prices.add("XYZ", D(3, 13), "102")
        row = self.w.api.get_positions("GEQ", "2026-03-13").body["XYZ"]
        self.assertEqual((row["unrealized"], row["quantity"]), ("850.00", "450"))

    def test_PNL1604_book_total_in_usd(self):
        self.w.buy(100, "10", D(3, 2))
        self.w.prices.add("IBM", D(3, 2), "11")
        self.w.buy(1000, "2500", D(3, 2), security="7203", currency="JPY")
        self.w.prices.add("7203", D(3, 2), "2600")
        self.w.fx.add("JPY", D(3, 1), "0.0066")
        self.assertEqual(self.w.api.get_book_total("GEQ", "2026-03-02").body["total_usd"], "760.00")
