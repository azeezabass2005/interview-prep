import unittest

from auction.house import AuctionHouse


class HiddenAuction(unittest.TestCase):
    def setUp(self):
        self.house = AuctionHouse()
        self.house.add_lot("L1", reserve_cents=10_000)

    def bids(self, *pairs):
        for bidder, amount in pairs:
            self.house.place_bid("L1", bidder, amount)
        return self.house.close("L1")

    def test_B1_tie_goes_to_earlier_bid(self):
        self.assertEqual(self.bids(("A", 15_000), ("B", 15_000)).winner, "A")

    def test_B2_hammer_capped_at_winners_bid(self):
        self.assertEqual(self.bids(("A", 15_000), ("B", 14_800)).hammer_cents, 15_000)

    def test_B3_latest_bid_counts(self):
        self.assertEqual(self.bids(("A", 20_000), ("B", 15_000), ("A", 12_000)).winner, "B")

    def test_B4_single_bid_pays_reserve(self):
        self.assertEqual(self.bids(("A", 15_000)).hammer_cents, 10_000)

    def test_B5_premium_on_hammer_price(self):
        self.assertEqual(self.bids(("A", 20_000), ("B", 12_000)).invoice_cents, 13_750)

    def test_G1_no_bids_after_close(self):
        self.house.close("L1")
        with self.assertRaises(Exception):
            self.house.place_bid("L1", "A", 50_000)
