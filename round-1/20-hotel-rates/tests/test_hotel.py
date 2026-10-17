import unittest
from datetime import date, datetime
from decimal import Decimal

from hotel import Hotel


class TestHotel(unittest.TestCase):
    def test_reservation_is_stored(self):
        hotel = Hotel({"KING": 2})
        r = hotel.book("r1", "ana", "KING", date(2026, 6, 10), date(2026, 6, 12), "BAR", datetime(2026, 6, 1, 9))
        self.assertEqual(hotel.reservations["r1"].status, "BOOKED")


if __name__ == "__main__":
    unittest.main()
