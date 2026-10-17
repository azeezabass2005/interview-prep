import unittest
from datetime import datetime

from gateway import Gateway

T0 = datetime(2026, 5, 4, 12, 0, 10)


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class Backend:
    def __init__(self, statuses=None):
        self.statuses = list(statuses or [])
        self.calls = 0

    def __call__(self, path):
        self.calls += 1
        return self.statuses.pop(0) if self.statuses else 200


def gateway(now=T0):
    clock = Clock(now)
    gw = Gateway(clock)
    gw.add_backend("core", Backend())
    gw.add_backend("search", Backend())
    gw.add_route("/v1", "core")
    gw.add_route("/v1/search", "search", cost=5)
    gw.add_key("k1", "FREE")
    return gw, clock


class HiddenGateway(unittest.TestCase):
    def test_B1_longest_prefix_wins(self):
        gw, _ = gateway()
        gw.handle("k1", "ip", "/v1/search/news")
        self.assertEqual(gw.backends["search"].calls, 1)

    def test_B2_route_cost_counts(self):
        gw, _ = gateway()
        for _ in range(12):
            gw.handle("k1", "ip", "/v1/search/news")
        self.assertEqual(gw.handle("k1", "ip", "/v1/search/news")[0], 429)

    def test_B3_retry_after_until_next_window(self):
        gw, clock = gateway(datetime(2026, 5, 4, 12, 0, 0))
        for _ in range(60):
            gw.handle("k1", "ip", "/v1/x")
        clock.current = datetime(2026, 5, 4, 12, 0, 45)
        self.assertEqual(gw.handle("k1", "ip", "/v1/x"), (429, {"Retry-After": "15"}))

    def test_B4_blocked_ip_checked_first(self):
        gw, _ = gateway()
        gw.block("6.6.6.6")
        self.assertEqual(gw.handle("unknown", "6.6.6.6", "/v1/x")[0], 403)

    def test_B5_success_resets_failure_count(self):
        gw, _ = gateway()
        gw.backends["core"] = Backend([500, 500, 500, 500, 200, 500, 200])
        for _ in range(6):
            gw.handle("k1", "ip", "/v1/x")
        self.assertEqual(gw.handle("k1", "ip", "/v1/x")[0], 200)
