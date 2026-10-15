import unittest
from decimal import Decimal as D

from payroll.models import Shift
from payroll.pay import weekly_pay
from tests.helpers import MONDAY, shift

RATE = D("20")


class TestPay(unittest.TestCase):
    def test_single_regular_day(self):
        self.assertEqual(weekly_pay(RATE, [shift(0, 9, 8)]), D("160.00"))

    def test_daily_overtime(self):
        self.assertEqual(weekly_pay(RATE, [shift(0, 8, 10)]), D("220.00"))

    def test_weekly_overtime_six_days(self):
        self.assertEqual(weekly_pay(RATE, [shift(d, 9, 8) for d in range(6)]), D("1040.00"))

    def test_empty_week(self):
        self.assertEqual(weekly_pay(RATE, []), D("0.00"))

    def test_shift_must_end_after_start(self):
        with self.assertRaises(ValueError):
            Shift(MONDAY, MONDAY)


if __name__ == "__main__":
    unittest.main()
