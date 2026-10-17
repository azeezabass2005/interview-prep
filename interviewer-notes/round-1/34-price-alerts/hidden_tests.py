import unittest
from datetime import datetime, timezone

from alerts import AlertService


def utc(h, m=0, day=15):
    return datetime(2026, 1, day, h, m, tzinfo=timezone.utc)


def service():
    svc = AlertService()
    svc.add_user("ana", "Europe/London")
    svc.add_user("ben", "Europe/London")
    return svc


class HiddenAlerts(unittest.TestCase):
    def test_B1_exactly_at_threshold_fires(self):
        svc = service()
        svc.on_tick("ABC", 95, utc(10))
        svc.create("a1", "ana", "ABC", "ABOVE", 100)
        self.assertEqual(len(svc.on_tick("ABC", 100, utc(11))), 1)

    def test_B2_no_fire_if_condition_already_held(self):
        svc = service()
        svc.on_tick("ABC", 105, utc(10))
        svc.create("a1", "ana", "ABC", "ABOVE", 100)
        self.assertEqual(svc.on_tick("ABC", 106, utc(11)), [])

    def test_B3_one_shot_fires_once(self):
        svc = service()
        svc.on_tick("ABC", 95, utc(10))
        svc.create("a1", "ana", "ABC", "ABOVE", 100)
        for price in (101, 99, 101):
            svc.on_tick("ABC", price, utc(11))
        self.assertEqual(len(svc.notifications), 1)

    def test_B4_quiet_hours_cross_midnight(self):
        svc = service()
        svc.on_tick("ABC", 95, utc(10))
        svc.create("a1", "ana", "ABC", "ABOVE", 100)
        [n] = svc.on_tick("ABC", 101, utc(23))
        self.assertEqual(n.deliver_at, datetime(2026, 1, 16, 7, 0, tzinfo=timezone.utc))

    def test_B5_daily_cap_is_per_user(self):
        svc = service()
        for i, sym in enumerate(("A", "B", "C")):
            svc.on_tick(sym, 95, utc(9))
            svc.create(f"a{i}", "ana", sym, "ABOVE", 100)
            svc.on_tick(sym, 101, utc(10))
        svc.on_tick("D", 95, utc(9))
        svc.create("b1", "ben", "D", "ABOVE", 100)
        [n] = svc.on_tick("D", 101, utc(11))
        self.assertEqual(n.status, "SCHEDULED")
