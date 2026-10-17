import unittest
from datetime import date
from decimal import Decimal

from bonds import Bond, Desk


def bond(maturity, convention="30/360", rate="0.06"):
    return Bond(Decimal("1000"), Decimal(rate), 2, maturity, convention)


class HiddenBonds(unittest.TestCase):
    def test_B1_holidays_are_not_business_days(self):
        desk = Desk(holidays=[date(2026, 12, 25)])
        self.assertEqual(desk.settlement_date(date(2026, 12, 23)), date(2026, 12, 28))

    def test_B2_30_360_day_31_start(self):
        b = bond(date(2030, 7, 31))
        self.assertEqual(round(b.accrued(date(2026, 2, 15)), 2), Decimal("2.50"))

    def test_B3_act_360_divides_by_360(self):
        b = bond(date(2030, 6, 15), "ACT/360")
        self.assertEqual(round(b.accrued(date(2026, 7, 15)), 2), Decimal("5.00"))

    def test_B4_settling_on_coupon_date_accrues_nothing(self):
        self.assertEqual(bond(date(2030, 6, 15)).accrued(date(2026, 6, 15)), 0)

    def test_B5_end_of_month_schedule_does_not_drift(self):
        self.assertEqual(bond(date(2030, 8, 31)).previous_coupon(date(2026, 9, 10)), date(2026, 8, 31))
