import unittest
from datetime import datetime

from studio.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestStudio(unittest.TestCase):
    def test_book_until_full(self):
        api = build_app(FakeClock(datetime(2026, 9, 1, 8, 0)))
        api.add_class("spin", "2026-09-02T18:00", 1)
        api.join("ana", "UNLIMITED")
        api.join("sam", "UNLIMITED")
        self.assertEqual(api.book("spin", "ana")[1]["status"], "BOOKED")
        self.assertEqual(api.book("spin", "sam")[1]["status"], "WAITLISTED")


if __name__ == "__main__":
    unittest.main()
