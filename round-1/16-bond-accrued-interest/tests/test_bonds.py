import unittest
from datetime import date
from decimal import Decimal

from bonds import Bond, Desk


class TestBonds(unittest.TestCase):
    def test_settles_two_days_later(self):
        self.assertEqual(Desk().settlement_date(date(2026, 6, 1)), date(2026, 6, 3))


if __name__ == "__main__":
    unittest.main()
