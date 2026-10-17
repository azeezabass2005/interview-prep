import unittest
from datetime import date, datetime
from decimal import Decimal

from hotel import Hotel

BOOKED_AT = datetime(2026, 5, 1, 9)


class HiddenHotel(unittest.TestCase):
    def test_B1_check_out_day_is_not_a_night(self):
        r = Hotel({"KING": 2}).book("r1", "ana", "KING", date(2026, 6, 10), date(2026, 6, 12), "BAR", BOOKED_AT)
        self.assertEqual(r.total, Decimal("336.00"))

    def test_B2_friday_and_saturday_are_weekend(self):
        hotel = Hotel({"KING": 2})
        self.assertEqual(hotel.nightly_rate(date(2026, 6, 12), "BAR"), Decimal("190.00"))
        self.assertEqual(hotel.nightly_rate(date(2026, 6, 14), "BAR"), Decimal("150.00"))

    def test_B3_advance_with_exactly_14_days(self):
        hotel = Hotel({"KING": 2})
        r = hotel.book("r1", "ana", "KING", date(2026, 6, 10), date(2026, 6, 11), "ADVANCE", datetime(2026, 5, 27, 9))
        self.assertEqual(r.plan, "ADVANCE")

    def test_B4_every_night_must_be_free(self):
        hotel = Hotel({"KING": 1})
        hotel.book("r1", "ana", "KING", date(2026, 6, 10), date(2026, 6, 12), "BAR", BOOKED_AT)
        with self.assertRaises(Exception):
            hotel.book("r2", "ben", "KING", date(2026, 6, 9), date(2026, 6, 11), "BAR", BOOKED_AT)

    def test_B5_free_cancel_until_48h_before_15_00(self):
        hotel = Hotel({"KING": 2})
        hotel.book("r1", "ana", "KING", date(2026, 6, 10), date(2026, 6, 11), "BAR", BOOKED_AT)
        self.assertEqual(hotel.cancel("r1", datetime(2026, 6, 8, 14, 0)), Decimal("0.00"))
