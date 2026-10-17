import unittest
from datetime import datetime, timezone

from meetings import Calendar


def utc(h, m=0):
    return datetime(2026, 3, 16, h, m, tzinfo=timezone.utc)


def calendar():
    cal = Calendar()
    for name, tz in (("ana", "Europe/London"), ("dan", "Europe/London"), ("eve", "Europe/London"), ("ben", "America/New_York")):
        cal.add_user(name, tz)
    return cal


class HiddenMeetings(unittest.TestCase):
    def test_B1_request_ids_are_per_organizer(self):
        cal = calendar()
        cal.request("ana", ["dan"], utc(10), 30, "r-1")
        m = cal.request("eve", [], utc(14), 30, "r-1")
        self.assertEqual((m.organizer, len(cal.meetings)), ("eve", 2))

    def test_B2_back_to_back_is_not_a_conflict(self):
        cal = calendar()
        cal.request("ana", ["dan"], utc(10), 60, "r-1")
        self.assertEqual(cal.request("eve", ["dan"], utc(11), 30, "r-2").status, "CONFIRMED")

    def test_B3_working_hours_in_local_time(self):
        cal = calendar()
        self.assertEqual(cal.request("ben", [], utc(20), 30, "r-1").status, "CONFIRMED")

    def test_B4_organizer_conflicts_count(self):
        cal = calendar()
        cal.request("ana", [], utc(10), 60, "r-1")
        self.assertEqual(cal.request("ana", ["dan"], utc(10, 30), 30, "r-2").status, "PENDING")

    def test_B5_cancel_confirms_pending_meetings(self):
        cal = calendar()
        first = cal.request("dan", ["ana"], utc(10), 60, "r-1")
        second = cal.request("eve", ["ana"], utc(10, 30), 30, "r-2")
        cal.cancel(first.meeting_id)
        self.assertEqual(second.status, "CONFIRMED")
