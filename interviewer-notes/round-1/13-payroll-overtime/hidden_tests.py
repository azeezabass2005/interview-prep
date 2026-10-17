import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal

from payroll import Payroll

MON = date(2026, 3, 2)


def at(day_offset, hour, minute=0):
    return datetime(2026, 3, 2, hour, minute) + timedelta(days=day_offset)


def staff():
    p = Payroll()
    p.set_rate("ana", date(2026, 1, 1), 20)
    return p


class HiddenPayroll(unittest.TestCase):
    def test_B1_six_hours_has_no_break(self):
        p = staff()
        p.add_shift("ana", at(0, 9), at(0, 15))
        self.assertEqual(p.week("ana", MON)["gross"], Decimal("120.00"))

    def test_B2_double_time_after_12_hours(self):
        p = staff()
        p.add_shift("ana", at(0, 6), at(0, 20))
        self.assertEqual(p.week("ana", MON)["gross"], Decimal("340.00"))

    def test_B3_daily_overtime_not_counted_toward_40(self):
        p = staff()
        for d in range(5):
            p.add_shift("ana", at(d, 7), at(d, 17, 30))
        self.assertEqual(p.week("ana", MON)["gross"], Decimal("1100.00"))

    def test_B4_rate_in_effect_on_the_day(self):
        p = staff()
        p.set_rate("ana", date(2026, 3, 9), 25)
        p.add_shift("ana", at(0, 9), at(0, 17, 30))
        self.assertEqual(p.week("ana", MON)["gross"], Decimal("160.00"))

    def test_B5_night_shift_belongs_to_start_day(self):
        p = staff()
        p.add_shift("ana", at(0, 20), at(1, 2))
        p.add_shift("ana", at(1, 8), at(1, 16, 30))
        self.assertEqual(p.week("ana", MON)["gross"], Decimal("280.00"))
