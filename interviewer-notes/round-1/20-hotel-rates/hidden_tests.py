import unittest
from datetime import date, datetime
from decimal import Decimal as D

from hotel.cancellation import refund
from hotel.pricing import los_discount_rate, nightly_rates, quote

MONDAY = date(2026, 6, 1)
THURSDAY = date(2026, 6, 4)


class HiddenHotel(unittest.TestCase):
    def test_B1_friday_and_saturday_are_weekend_nights(self):
        self.assertEqual(nightly_rates("DELUXE", THURSDAY, 3), [D("220"), D("264.00"), D("264.00")])

    def test_B2_seven_nights_gets_long_stay_rate(self):
        self.assertEqual(los_discount_rate(7), D("0.15"))

    def test_B3_promo_after_length_of_stay_discount(self):
        self.assertEqual(quote("STANDARD", MONDAY, 3, "SAVE50").room_total, D("377.50"))

    def test_B4_city_fee_not_taxed(self):
        self.assertEqual(quote("STANDARD", MONDAY, 1).total, D("175.63"))

    def test_B5_refund_window_measured_to_3pm(self):
        q = quote("DELUXE", THURSDAY, 3)
        self.assertEqual(refund(q, datetime(2026, 5, 28, 10, 0)), q.total)

    def test_spec_example(self):
        self.assertEqual(quote("DELUXE", THURSDAY, 3).total, D("825.91"))
