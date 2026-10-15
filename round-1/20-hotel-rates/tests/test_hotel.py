import unittest
from datetime import date, datetime
from decimal import Decimal as D

from hotel.cancellation import refund
from hotel.pricing import los_discount_rate, nightly_rates, quote

MONDAY = date(2026, 6, 1)


class TestPricing(unittest.TestCase):
    def test_weekday_rates(self):
        self.assertEqual(nightly_rates("STANDARD", MONDAY, 2), [D("150"), D("150")])

    def test_short_stay_no_discount(self):
        q = quote("STANDARD", MONDAY, 2)
        self.assertEqual(q.room_total, D("300"))
        self.assertEqual(q.city_fee, D("7.00"))

    def test_three_nights_five_percent(self):
        self.assertEqual(los_discount_rate(3), D("0.05"))

    def test_validation(self):
        with self.assertRaises(ValueError):
            quote("STANDARD", MONDAY, 0)
        with self.assertRaises(ValueError):
            quote("PENTHOUSE", MONDAY, 1)


class TestCancellation(unittest.TestCase):
    def test_no_refund_inside_48_hours(self):
        q = quote("STANDARD", MONDAY, 2)
        self.assertEqual(refund(q, datetime(2026, 5, 31, 12, 0)), D("0.00"))

    def test_full_refund_a_month_ahead(self):
        q = quote("STANDARD", MONDAY, 2)
        self.assertEqual(refund(q, datetime(2026, 5, 1, 9, 0)), q.total)


if __name__ == "__main__":
    unittest.main()
