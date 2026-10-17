import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from studio import Studio

START = datetime(2026, 9, 2, 18, 0)


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


def studio(capacity=1):
    clock = Clock(START - timedelta(days=1))
    s = Studio(clock)
    s.add_class("spin", START, capacity)
    for name in ("ana", "ben", "cat"):
        s.join(name, "UNLIMITED")
    s.join("pam", "PACK", 5)
    return s, clock


class HiddenStudio(unittest.TestCase):
    def test_B1_no_second_place_from_the_waitlist(self):
        s, _ = studio()
        s.book("spin", "ana")
        s.book("spin", "ben")
        with self.assertRaises(Exception):
            s.book("spin", "ben")

    def test_B2_first_on_waitlist_promoted(self):
        s, clock = studio()
        s.book("spin", "ana")
        s.book("spin", "ben")
        s.book("spin", "cat")
        clock.current = START - timedelta(hours=20)
        s.cancel("spin", "ana")
        self.assertEqual(s.classes["spin"].booked, ["ben"])

    def test_B3_exactly_12_hours_is_free(self):
        s, clock = studio()
        s.book("spin", "ana")
        clock.current = START - timedelta(hours=12)
        self.assertEqual(s.cancel("spin", "ana"), Decimal("0.00"))

    def test_B4_early_cancel_refunds_credit(self):
        s, _ = studio(5)
        s.book("spin", "pam")
        s.cancel("spin", "pam")
        self.assertEqual(s.members["pam"].credits, 5)

    def test_B5_no_promotion_in_last_hour(self):
        s, clock = studio()
        s.book("spin", "ana")
        s.book("spin", "ben")
        clock.current = START - timedelta(minutes=30)
        s.cancel("spin", "ana")
        self.assertEqual(s.classes["spin"].booked, [])
