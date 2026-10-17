import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from quotes import Quote, QuoteCache, VendorError

T0 = datetime(2026, 5, 4, 12, 0, 0)


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class Vendor:
    def __init__(self, clock, lag=timedelta(0)):
        self.clock = clock
        self.lag = lag
        self.calls = 0
        self.failing = False

    def fetch(self, symbol):
        self.calls += 1
        if self.failing:
            raise VendorError("vendor down")
        return Quote(symbol.upper(), Decimal("100"), self.clock.now() - self.lag)


def setup(capacity=1000, lag=timedelta(0)):
    clock = Clock(T0)
    vendor = Vendor(clock, lag)
    return QuoteCache(vendor, clock, capacity), vendor, clock


class HiddenQuotes(unittest.TestCase):
    def test_B1_five_seconds_old_is_not_fresh(self):
        cache, vendor, clock = setup()
        cache.get("AAPL")
        clock.current = T0 + timedelta(seconds=5)
        cache.get("AAPL")
        self.assertEqual(vendor.calls, 2)

    def test_B2_symbols_are_normalised(self):
        cache, vendor, _ = setup()
        cache.get("AAPL")
        cache.get(" aapl")
        self.assertEqual(vendor.calls, 1)

    def test_B3_no_stale_quote_after_60_seconds(self):
        cache, vendor, clock = setup()
        cache.get("AAPL")
        vendor.failing = True
        clock.current = T0 + timedelta(seconds=120)
        with self.assertRaises(VendorError):
            cache.get("AAPL")

    def test_B4_least_recently_used_is_evicted(self):
        cache, vendor, _ = setup(capacity=3)
        for s in ("A", "B", "C", "A", "D", "A"):
            cache.get(s)
        self.assertEqual(vendor.calls, 4)

    def test_B5_freshness_from_fetch_time(self):
        cache, vendor, clock = setup(lag=timedelta(seconds=10))
        cache.get("AAPL")
        clock.current = T0 + timedelta(seconds=1)
        cache.get("AAPL")
        self.assertEqual(vendor.calls, 1)
