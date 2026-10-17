import unittest
from decimal import Decimal

from pnl import PnlService


class TestPnl(unittest.TestCase):
    def test_unrealized_on_one_lot(self):
        p = PnlService()
        p.buy("ABC", 10, "100")
        self.assertEqual(p.unrealized("ABC", "110"), Decimal("100.00"))


if __name__ == "__main__":
    unittest.main()
