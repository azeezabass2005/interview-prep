import unittest
from datetime import datetime, timezone

from rooms import RoomService


def utc(day, h, m=0):
    return datetime(2026, 3, day, h, m, tzinfo=timezone.utc)


class TestRooms(unittest.TestCase):
    def test_london_booking(self):
        svc = RoomService()
        svc.add_room("Thames", "Europe/London", 8)
        b = svc.book("Thames", utc(16, 10), utc(16, 11), "ana", utc(15, 9))
        self.assertEqual(b.room, "Thames")


if __name__ == "__main__":
    unittest.main()
