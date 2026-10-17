import unittest
from datetime import datetime
from decimal import Decimal

from auction import SilentAuction

CLOSE = datetime(2026, 6, 1, 20, 0)


class TestAuction(unittest.TestCase):
    def test_single_bidder_pays_start(self):
        a = SilentAuction()
        a.add_item("vase", 50, CLOSE)
        a.bid("vase", "ana", 80, datetime(2026, 6, 1, 18, 0))
        self.assertEqual(a.price("vase"), Decimal("50"))


if __name__ == "__main__":
    unittest.main()
