import unittest

from tests.helpers import D, World


class TestPnl(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_single_lot_round_trip(self):
        self.w.buy(100, "10", D(3, 2))
        self.w.sell(100, "12", D(3, 5))
        row = self.w.api.get_positions("GEQ", "2026-03-06").body["IBM"]
        self.assertEqual((row["realized"], row["unrealized"], row["quantity"]), ("200.00", "0.00", "0"))

    def test_unrealized_with_one_price(self):
        self.w.buy(100, "10", D(3, 2))
        self.w.prices.add("IBM", D(3, 2), "11")
        self.assertEqual(self.w.api.get_positions("GEQ", "2026-03-02").body["IBM"]["unrealized"], "100.00")

    def test_short_selling_rejected(self):
        self.w.buy(10, "10", D(3, 2))
        self.w.sell(20, "10", D(3, 3))
        self.assertEqual(self.w.api.get_positions("GEQ", "2026-03-04").status, 400)

    def test_usd_book_total(self):
        self.w.buy(100, "10", D(3, 2))
        self.w.prices.add("IBM", D(3, 2), "11")
        self.assertEqual(self.w.api.get_book_total("GEQ", "2026-03-02").body["total_usd"], "100.00")


if __name__ == "__main__":
    unittest.main()
