import unittest
from datetime import datetime
from decimal import Decimal

from quotes import Quote, QuoteCache

T0 = datetime(2026, 5, 4, 12, 0, 0)


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class Vendor:
    def __init__(self, clock):
        self.clock = clock
        self.calls = 0

    def fetch(self, symbol):
        self.calls += 1
        return Quote(symbol.upper(), Decimal("190.12"), self.clock.now())


class TestQuotes(unittest.TestCase):
    def test_first_get_calls_vendor(self):
        clock = Clock(T0)
        vendor = Vendor(clock)
        cache = QuoteCache(vendor, clock)
        self.assertEqual(cache.get("AAPL").price, Decimal("190.12"))
        self.assertEqual(vendor.calls, 1)


if __name__ == "__main__":
    unittest.main()
