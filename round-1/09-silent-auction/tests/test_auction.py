import unittest

from auction.house import AuctionHouse
from auction.models import AuctionError


class TestAuction(unittest.TestCase):
    def setUp(self):
        self.house = AuctionHouse()

    def test_first_example(self):
        self.house.add_lot("L1", reserve_cents=10_000)
        self.house.place_bid("L1", "A", 15_000)
        self.house.place_bid("L1", "B", 18_000)
        self.house.place_bid("L1", "C", 17_000)
        result = self.house.close("L1")
        self.assertEqual(result.winner, "B")
        self.assertEqual(result.hammer_cents, 17_500)

    def test_unsold_below_reserve(self):
        self.house.add_lot("L1", reserve_cents=10_000)
        self.house.place_bid("L1", "A", 9_000)
        self.assertIsNone(self.house.close("L1"))

    def test_no_bids(self):
        self.house.add_lot("L1")
        self.assertIsNone(self.house.close("L1"))

    def test_rejects_non_positive_bid(self):
        self.house.add_lot("L1")
        with self.assertRaises(AuctionError):
            self.house.place_bid("L1", "A", 0)

    def test_duplicate_lot(self):
        self.house.add_lot("L1")
        with self.assertRaises(AuctionError):
            self.house.add_lot("L1")


if __name__ == "__main__":
    unittest.main()
