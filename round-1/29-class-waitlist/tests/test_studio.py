import unittest
from datetime import datetime

from studio import Studio


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestStudio(unittest.TestCase):
    def test_full_class_waitlists(self):
        studio = Studio(Clock(datetime(2026, 9, 1, 8, 0)))
        studio.add_class("spin", datetime(2026, 9, 2, 18, 0), 1)
        studio.join("ana", "UNLIMITED")
        studio.join("ben", "UNLIMITED")
        self.assertEqual((studio.book("spin", "ana"), studio.book("spin", "ben")), ("BOOKED", "WAITLISTED"))


if __name__ == "__main__":
    unittest.main()
