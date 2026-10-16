import unittest
from datetime import datetime, timedelta

from studio.app import build_app

START = datetime(2026, 9, 2, 18, 0)


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


def studio():
    clock = FakeClock(START - timedelta(days=1))
    api = build_app(clock)
    api.add_class("spin", START.isoformat(), 1)
    api.add_class("yoga", START.isoformat(), 5)
    for m, plan, credits in (("ana", "UNLIMITED", 0), ("sam", "UNLIMITED", 0), ("pia", "PREMIUM", 0), ("pk", "PACK", 5)):
        api.join(m, plan, credits)
    return api, clock


class HiddenStudio(unittest.TestCase):
    def test_B1_premium_first(self):
        api, clock = studio()
        api.book("spin", "ana")
        api.book("spin", "sam")
        api.book("spin", "pia")
        clock.current = START - timedelta(hours=20)
        api.cancel("spin", "ana")
        self.assertEqual(api.roster("spin")[1]["booked"], ["pia"])

    def test_B2_promoted_leaves_waitlist(self):
        api, clock = studio()
        api.book("spin", "ana")
        api.book("spin", "sam")
        api.cancel("spin", "ana")
        self.assertEqual(api.roster("spin")[1]["waitlist"], [])

    def test_B3_no_promotion_in_last_hour(self):
        api, clock = studio()
        api.book("spin", "ana")
        api.book("spin", "sam")
        clock.current = START - timedelta(minutes=30)
        api.cancel("spin", "ana")
        self.assertEqual(api.roster("spin")[1]["booked"], [])

    def test_B4_late_cancel_forfeits_credit(self):
        api, clock = studio()
        api.book("yoga", "pk")
        clock.current = START - timedelta(hours=2)
        api.cancel("yoga", "pk")
        self.assertEqual(api.member("pk")[1]["credits"], 4)

    def test_B5_pack_member_without_credits_skipped(self):
        api, clock = studio()
        api.join("pk", "PACK", 1)
        api.book("spin", "ana")
        api.book("spin", "pk")
        api.book("yoga", "pk")
        api.book("spin", "sam")
        api.cancel("spin", "ana")
        roster = api.roster("spin")[1]
        self.assertEqual((roster["booked"], roster["waitlist"]), (["sam"], ["pk"]))
        self.assertEqual(api.member("pk")[1]["credits"], 0)
