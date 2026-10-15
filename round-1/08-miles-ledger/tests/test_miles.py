import unittest
from datetime import date
from decimal import Decimal

from miles.account import MilesAccount
from miles.earning import miles_for_fare
from miles.models import InsufficientMiles, Member


class TestEarning(unittest.TestCase):
    def test_base_member_five_per_dollar(self):
        self.assertEqual(miles_for_fare(Decimal("100"), "BASE"), 500)

    def test_unknown_tier_rejected(self):
        with self.assertRaises(ValueError):
            Member("m1", "DIAMOND")


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = MilesAccount(Member("m1", "BASE"))

    def test_balance_sums_lots(self):
        self.account.earn(Decimal("100"), date(2025, 1, 10))
        self.account.earn(Decimal("200"), date(2025, 2, 10))
        self.assertEqual(self.account.balance(date(2025, 3, 1)), 1500)

    def test_redeem_reduces_balance(self):
        self.account.earn(Decimal("200"), date(2025, 1, 10))
        self.account.redeem(400, date(2025, 3, 1))
        self.assertEqual(self.account.balance(date(2025, 3, 1)), 600)

    def test_redeem_must_be_positive(self):
        with self.assertRaises(ValueError):
            self.account.redeem(0, date(2025, 3, 1))

    def test_not_enough_miles(self):
        with self.assertRaises(InsufficientMiles):
            self.account.redeem(10, date(2025, 3, 1))

    def test_long_expired_lot(self):
        self.account.earn(Decimal("100"), date(2020, 1, 10))
        self.assertEqual(self.account.balance(date(2025, 1, 1)), 0)


if __name__ == "__main__":
    unittest.main()
