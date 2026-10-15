import threading
import unittest
from datetime import datetime
from unittest import mock

from rooms.errors import Conflict
from rooms.repositories.bookings import BookingRepository
from tests.helpers import World


class HiddenRooms(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_ROOM1801_concurrent_overlapping_bookings(self):
        a, b = self.w.service(), self.w.service()
        barrier = threading.Barrier(2, timeout=3)
        original = BookingRepository.overlapping
        calls = {"n": 0}
        lock = threading.Lock()

        def paused(repo, room_id, start, end):
            result = original(repo, room_id, start, end)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        outcomes = []

        def run(svc, start, end):
            try:
                svc.book("thames4", "ann", ["bob"], datetime.fromisoformat(start), datetime.fromisoformat(end))
                outcomes.append("ok")
            except Conflict:
                outcomes.append("conflict")

        with mock.patch.object(BookingRepository, "overlapping", paused):
            threads = [threading.Thread(target=run, args=(a, "2026-05-18T10:00", "2026-05-18T11:00")),
                       threading.Thread(target=run, args=(b, "2026-05-18T10:30", "2026-05-18T11:30"))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(sorted(outcomes), ["conflict", "ok"])
        self.assertEqual(self.w.bookings.count("thames4"), 1)

    def test_ROOM1802_series_includes_until_date(self):
        resp = self.w.api.post_series("ann", {"room_id": "thames4", "first_start": "2026-06-01T09:00", "minutes": 60,
                                              "until": "2026-06-29", "attendees": ["bob"]})
        self.assertEqual(len(resp.body["booking_ids"]), 5)

    def test_ROOM1803_capacity_includes_organizer(self):
        six = [f"p{i}" for i in range(6)]
        self.assertEqual(self.w.book("2026-05-18T01:00", "2026-05-18T02:00", room="shibuya2", attendees=six).status, 400)
        self.assertEqual(self.w.book("2026-05-18T01:00", "2026-05-18T02:00", room="shibuya2", attendees=six[:5]).status, 201)

    def test_ROOM1804_schedule_uses_room_local_day(self):
        self.w.book("2026-05-20T23:30", "2026-05-21T00:30", room="shibuya2")  # 08:30 JST on 21 May
        self.assertEqual(len(self.w.api.get_schedule("shibuya2", "2026-05-21").body["bookings"]), 1)
        self.assertEqual(len(self.w.api.get_schedule("shibuya2", "2026-05-20").body["bookings"]), 0)
