import unittest

from tests.helpers import World


class TestRooms(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_book(self):
        self.assertEqual(self.w.book("2026-05-18T09:00", "2026-05-18T10:00").status, 201)

    def test_overlap_rejected(self):
        self.w.book("2026-05-18T09:00", "2026-05-18T10:00")
        self.assertEqual(self.w.book("2026-05-18T09:30", "2026-05-18T10:30").status, 409)

    def test_back_to_back_allowed(self):
        self.w.book("2026-05-18T09:00", "2026-05-18T10:00")
        self.assertEqual(self.w.book("2026-05-18T10:00", "2026-05-18T11:00").status, 201)

    def test_invalid_times(self):
        self.assertEqual(self.w.book("2026-05-18T10:00", "2026-05-18T09:00").status, 400)

    def test_weekly_series(self):
        resp = self.w.api.post_series("ann", {"room_id": "thames4", "first_start": "2026-06-01T09:00", "minutes": 60,
                                              "until": "2026-06-20", "attendees": ["bob"]})
        self.assertEqual(len(resp.body["booking_ids"]), 3)

    def test_london_schedule_daytime(self):
        self.w.book("2026-05-18T09:00", "2026-05-18T10:00")
        self.assertEqual(len(self.w.api.get_schedule("thames4", "2026-05-18").body["bookings"]), 1)


if __name__ == "__main__":
    unittest.main()
