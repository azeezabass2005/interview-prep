import unittest
from datetime import datetime, timezone

from alerts import AlertService


def utc(h, m=0):
    return datetime(2026, 1, 15, h, m, tzinfo=timezone.utc)


class TestAlerts(unittest.TestCase):
    def test_below_alert_fires(self):
        svc = AlertService()
        svc.add_user("ana", "Europe/London")
        svc.on_tick("ABC", 105, utc(10))
        svc.create("a1", "ana", "ABC", "BELOW", 100)
        self.assertEqual(len(svc.on_tick("ABC", 99, utc(11))), 1)


if __name__ == "__main__":
    unittest.main()
