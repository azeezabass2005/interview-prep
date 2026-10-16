import unittest
from decimal import Decimal

from metering.app import build_app

T0 = Decimal("1772323200")


class FakeClock:
    def __init__(self):
        self.t = T0

    def time(self):
        return self.t

    def at(self, seconds):
        self.t = T0 + Decimal(str(seconds))


def world(plan="FREE"):
    clock = FakeClock()
    api, store = build_app(clock)
    api.register("c", plan)
    return api, store, clock


def allowed(api, endpoint="/quote"):
    return api.request("c", endpoint)[1]["allowed"]


class HiddenMetering(unittest.TestCase):
    def test_B1_refill_capped(self):
        api, _, clock = world()
        for _ in range(10):
            allowed(api)
        clock.at(100)
        self.assertEqual([allowed(api) for _ in range(11)], [True] * 10 + [False])

    def test_B2_retry_after_uses_refill_rate(self):
        api, _, _ = world("PRO")
        for _ in range(5):
            allowed(api, "/bulk")
        self.assertEqual(api.request("c", "/bulk")[1]["retry_after"], "1.0")

    def test_B3_fractional_refill(self):
        api, _, clock = world()
        for _ in range(10):
            allowed(api)
        clock.at("1.5")
        self.assertTrue(allowed(api))
        clock.at("2.0")
        self.assertTrue(allowed(api))

    def test_B4_rejected_requests_not_metered(self):
        api, store, _ = world()
        for _ in range(11):
            allowed(api)
        month = next(iter(store.client("c").usage))
        self.assertEqual(api.invoice("c", month)[1]["units"], 10)

    def test_B5_overage_only_above_allowance(self):
        api, store, _ = world("PRO")
        store.client("c").usage["2026-03"] = 1_000_500
        self.assertEqual(api.invoice("c", "2026-03")[1]["total"], "500.50")
