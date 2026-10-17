import unittest
from datetime import datetime, timezone

from meetings import Calendar


class TestMeetings(unittest.TestCase):
    def test_simple_meeting_confirmed(self):
        cal = Calendar()
        cal.add_user("ana", "Europe/London")
        cal.add_user("dan", "Europe/London")
        m = cal.request("ana", ["dan"], datetime(2026, 3, 16, 10, 0, tzinfo=timezone.utc), 60, "r-1")
        self.assertEqual(m.status, "CONFIRMED")


if __name__ == "__main__":
    unittest.main()
