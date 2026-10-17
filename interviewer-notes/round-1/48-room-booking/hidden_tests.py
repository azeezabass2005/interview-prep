import unittest
from datetime import datetime, timezone

from rooms import RoomService


def utc(day, h, m=0):
    return datetime(2026, 3, day, h, m, tzinfo=timezone.utc)


def service():
    svc = RoomService()
    svc.add_room("Fuji", "Asia/Tokyo", 6)
    svc.add_room("Thames", "Europe/London", 8)
    return svc


class HiddenRooms(unittest.TestCase):
    def test_B1_hours_in_office_time(self):
        b = service().book("Fuji", utc(16, 0), utc(16, 1), "ken", utc(15, 0))
        self.assertEqual(b.room, "Fuji")

    def test_B2_four_hours_allowed(self):
        b = service().book("Thames", utc(16, 9), utc(16, 13), "ana", utc(15, 9))
        self.assertEqual(b.end - b.start, utc(16, 13) - utc(16, 9))

    def test_B3_no_show_released(self):
        svc = service()
        svc.book("Thames", utc(16, 10), utc(16, 11), "ana", utc(15, 9))
        b = svc.book("Thames", utc(16, 10, 15), utc(16, 11), "ben", utc(16, 10, 11))
        self.assertEqual(b.organizer, "ben")

    def test_B4_capacity_equal_to_attendees(self):
        self.assertIn("Thames", service().search(utc(16, 10), utc(16, 11), 8, utc(15, 9)))

    def test_B5_weekly_all_or_nothing(self):
        svc = service()
        svc.book("Thames", utc(23, 10), utc(23, 11), "ben", utc(15, 9))
        with self.assertRaises(Exception):
            svc.book_weekly("Thames", utc(16, 10), utc(16, 11), "ana", 3, utc(15, 9))
        self.assertEqual(len(svc.bookings), 1)
