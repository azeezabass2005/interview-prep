import unittest
from datetime import date
from decimal import Decimal as D

from bond.daycount import days_30_360
from bond.models import Bond
from bond.pricing import accrued_interest, settlement_date
from bond.schedule import previous_and_next

BOND = Bond(D("1000000"), D("0.05"), 2, date(2030, 5, 15))


class HiddenBond(unittest.TestCase):
    def test_B1_d2_adjusts_only_when_d1_is_30(self):
        self.assertEqual(days_30_360(date(2026, 1, 15), date(2026, 3, 31)), 76)
        self.assertEqual(days_30_360(date(2026, 1, 30), date(2026, 3, 31)), 60)

    def test_B2_end_of_month_rule(self):
        eom = Bond(D("1000000"), D("0.05"), 2, date(2030, 6, 30))
        self.assertEqual(previous_and_next(eom, date(2026, 1, 15))[0], date(2025, 12, 31))

    def test_B3_settlement_skips_weekend(self):
        self.assertEqual(settlement_date(date(2026, 3, 13)), date(2026, 3, 16))

    def test_B4_settle_on_coupon_date_accrues_nothing(self):
        self.assertEqual(accrued_interest(BOND, date(2026, 5, 15)), D("0.00"))

    def test_B5_spec_example_rounds_half_up(self):
        self.assertEqual(accrued_interest(BOND, date(2026, 3, 13)), D("16388.89"))
