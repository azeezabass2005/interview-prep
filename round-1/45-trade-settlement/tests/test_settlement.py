import unittest
from datetime import date

from settlement import Settlement


class TestSettlement(unittest.TestCase):
    def test_monday_trade_settles_tuesday(self):
        self.assertEqual(Settlement().settle_date(date(2026, 6, 29)), date(2026, 6, 30))


if __name__ == "__main__":
    unittest.main()
