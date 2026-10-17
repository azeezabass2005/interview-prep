import unittest
from datetime import datetime
from decimal import Decimal

from auction import SilentAuction

CLOSE = datetime(2026, 6, 1, 20, 0)
EARLY = datetime(2026, 6, 1, 18, 0)


def item(reserve=None):
    a = SilentAuction()
    a.add_item("vase", 50, CLOSE, reserve)
    return a


class HiddenAuction(unittest.TestCase):
    def test_B1_increment_at_100_is_10(self):
        a = item()
        a.bid("vase", "ana", 100, EARLY)
        a.bid("vase", "ben", 200, EARLY)
        self.assertEqual(a.price("vase"), Decimal("110"))

    def test_B2_price_capped_at_highest_max(self):
        a = item()
        a.bid("vase", "ana", 150, EARLY)
        a.bid("vase", "ben", 155, EARLY)
        self.assertEqual(a.price("vase"), Decimal("155"))

    def test_B3_first_bidder_wins_ties(self):
        a = item()
        a.bid("vase", "ana", 90, EARLY)
        a.bid("vase", "ben", 90, EARLY)
        self.assertEqual(a.leader("vase"), "ana")

    def test_B4_soft_close_from_bid_time(self):
        a = item()
        a.bid("vase", "ana", 60, datetime(2026, 6, 1, 19, 57))
        self.assertEqual(a.items["vase"].closes_at, datetime(2026, 6, 1, 20, 2))

    def test_B5_reserve_not_met_means_no_sale(self):
        a = item(reserve=300)
        a.bid("vase", "ana", 200, EARLY)
        self.assertIsNone(a.close("vase", CLOSE))
