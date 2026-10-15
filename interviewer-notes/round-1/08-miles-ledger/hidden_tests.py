import unittest
from datetime import date
from decimal import Decimal

from miles.account import MilesAccount
from miles.earning import miles_for_fare
from miles.models import InsufficientMiles, Member


class HiddenMiles(unittest.TestCase):
    def test_B1_gold_bonus_is_fifty_percent(self):
        self.assertEqual(miles_for_fare(Decimal("412.80"), "GOLD"), 3090)

    def test_B2_cents_do_not_earn(self):
        self.assertEqual(miles_for_fare(Decimal("100.90"), "BASE"), 500)

    def test_B3_oldest_miles_spent_first(self):
        account = MilesAccount(Member("m1", "BASE"))
        account.earn(Decimal("200"), date(2024, 1, 10))
        account.earn(Decimal("200"), date(2025, 1, 10))
        account.redeem(1000, date(2025, 2, 1))
        self.assertEqual(account.balance(date(2026, 2, 1)), 1000)

    def test_B4_unusable_on_anniversary(self):
        account = MilesAccount(Member("m1", "BASE"))
        account.earn(Decimal("100"), date(2024, 3, 1))
        self.assertEqual(account.balance(date(2026, 2, 28)), 500)
        self.assertEqual(account.balance(date(2026, 3, 1)), 0)

    def test_B5_rejected_redemption_spends_nothing(self):
        account = MilesAccount(Member("m1", "BASE"))
        account.earn(Decimal("100"), date(2025, 1, 10))
        with self.assertRaises(InsufficientMiles):
            account.redeem(800, date(2025, 2, 1))
        self.assertEqual(account.balance(date(2025, 2, 1)), 500)

    def test_G1_platinum_never_expires(self):
        account = MilesAccount(Member("m1", "PLATINUM"))
        lot = account.earn(Decimal("100"), date(2020, 1, 10))
        self.assertEqual(account.balance(date(2026, 1, 1)), lot.miles)
