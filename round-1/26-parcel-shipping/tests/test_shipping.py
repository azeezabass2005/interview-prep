import unittest
from decimal import Decimal

from shipping import Parcel, price


class TestShipping(unittest.TestCase):
    def test_small_budget_parcel(self):
        self.assertEqual(price("BUDGET", Parcel(Decimal("1"), 10, 10, 10), 1), Decimal("7.15"))


if __name__ == "__main__":
    unittest.main()
