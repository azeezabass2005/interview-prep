import unittest
from datetime import date
from decimal import Decimal as D

from bond.daycount import days_30_360
from bond.models import Bond
from bond.pricing import accrued_interest, settlement_amount, settlement_date
from bond.schedule import previous_and_next

BOND = Bond(D("1000000"), D("0.05"), 2, date(2030, 5, 15))


class TestDayCount(unittest.TestCase):
    def test_one_month(self):
        self.assertEqual(days_30_360(date(2026, 1, 15), date(2026, 2, 15)), 30)

    def test_start_on_31st(self):
        self.assertEqual(days_30_360(date(2026, 1, 31), date(2026, 3, 15)), 45)


class TestSchedule(unittest.TestCase):
    def test_mid_month_coupons(self):
        self.assertEqual(previous_and_next(BOND, date(2026, 3, 13)), (date(2025, 11, 15), date(2026, 5, 15)))

    def test_bad_frequency(self):
        with self.assertRaises(ValueError):
            Bond(D("100"), D("0.05"), 3, date(2030, 1, 1))


class TestPricing(unittest.TestCase):
    def test_settlement_next_weekday(self):
        self.assertEqual(settlement_date(date(2026, 3, 9)), date(2026, 3, 10))

    def test_accrued_whole_cents(self):
        self.assertEqual(accrued_interest(BOND, date(2026, 1, 15)), D("8333.33"))

    def test_settlement_amount(self):
        self.assertEqual(settlement_amount(BOND, D("99.5"), date(2026, 1, 15)), D("1003333.33"))


if __name__ == "__main__":
    unittest.main()
