import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from quota import Meter

T0 = datetime(2026, 1, 10, 12, 0, 0)


def meter(plan="FREE"):
    m = Meter()
    m.create_key("k", plan, T0)
    return m


def use(m, total, cost, start=T0):
    at = start
    for _ in range(total // cost):
        at += timedelta(seconds=3)
        assert m.request("k", at, cost) == 200
    return at


class HiddenQuota(unittest.TestCase):
    def test_B1_bucket_never_exceeds_capacity(self):
        m = meter()
        m.request("k", T0, 10)
        later = T0 + timedelta(seconds=10)
        m.request("k", later, 10)
        self.assertEqual(m.request("k", later, 1), 429)

    def test_B2_rejected_request_takes_no_tokens(self):
        m = meter()
        m.request("k", T0, 8)
        m.request("k", T0, 5)
        self.assertEqual(m.request("k", T0 + timedelta(seconds=1), 6), 200)

    def test_B3_usage_resets_each_month(self):
        m = meter()
        use(m, 1000, 10)
        m.request("k", datetime(2026, 2, 1, 0, 0, 1), 1)
        self.assertEqual(m.monthly_usage("k", "2026-02"), 1)

    def test_B4_free_hard_limit_is_1000(self):
        m = meter()
        at = use(m, 1000, 10)
        self.assertEqual(m.request("k", at + timedelta(seconds=3), 1), 429)

    def test_B5_overage_only_above_included(self):
        m = meter("PRO")
        use(m, 100_500, 50)
        self.assertEqual(m.invoice("k", "2026-01"), Decimal("50.00"))
