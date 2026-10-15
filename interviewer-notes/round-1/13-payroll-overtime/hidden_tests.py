import unittest
from decimal import Decimal as D

from payroll.pay import weekly_pay
from tests.helpers import shift

RATE = D("20")


class HiddenPayroll(unittest.TestCase):
    def test_B1_double_time_not_also_overtime(self):
        self.assertEqual(weekly_pay(RATE, [shift(0, 6, 14)]), D("360.00"))

    def test_B2_daily_overtime_not_counted_twice(self):
        self.assertEqual(weekly_pay(RATE, [shift(d, 8, 10) for d in range(5)]), D("1100.00"))

    def test_B3_overnight_shift_belongs_to_start_day(self):
        shifts = [shift(0, 20, 10), shift(1, 8, 8)]
        self.assertEqual(weekly_pay(RATE, shifts), D("380.00"))

    def test_B4_seventh_day_premium(self):
        shifts = [shift(d, 9, 8) for d in range(6)] + [shift(6, 8, 13)]
        self.assertEqual(weekly_pay(RATE, shifts), D("1480.00"))

    def test_B5_minutes_count(self):
        self.assertEqual(weekly_pay(RATE, [shift(0, 9, 7.5)]), D("150.00"))
