import unittest
from datetime import date
from decimal import Decimal

from drip import DripProcessor


class TestDrip(unittest.TestCase):
    def test_cash_dividend(self):
        d = DripProcessor()
        d.open_account("a1", "US")
        d.trade("a1", "XYZ", date(2026, 3, 1), 100)
        [p] = d.pay_dividend("XYZ", "0.25", date(2026, 3, 10), date(2026, 3, 15), "40")
        self.assertEqual(p["cash"], Decimal("25.00"))


if __name__ == "__main__":
    unittest.main()
