import os
import threading
import time
import unittest
from decimal import Decimal as D
from unittest import mock

from mdcache.api.handlers import format_ts
from mdcache.cache import TtlCache
from mdcache.models import VenueQuote
from tests.helpers import World


class HiddenMarketData(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_MD301_cache_expires_after_ttl(self):
        self.w.api.get_quote("IBM")
        self.w.clock.advance(3)
        self.w.provider.prices["IBM"] = "181.50"
        self.assertEqual(self.w.api.get_quote("IBM").body["last"], "181.50")
        self.assertEqual(len(self.w.provider.calls), 2)

    def test_MD302_single_flight_per_symbol(self):
        n = 5
        barrier = threading.Barrier(n, timeout=3)
        original = TtlCache.get
        seen = {"n": 0}
        lock = threading.Lock()

        def paused_get(cache, key):
            result = original(cache, key)
            with lock:
                seen["n"] += 1
                first_round = seen["n"] <= n
            if first_round:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        results, errors = [], []

        def worker():
            try:
                results.append(self.w.service.get_quote("AAPL"))
            except Exception as e:
                errors.append(e)

        with mock.patch.object(TtlCache, "get", paused_get):
            threads = [threading.Thread(target=worker) for _ in range(n)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(errors, [])
        self.assertEqual(self.w.provider.calls, ["AAPL"])
        self.assertEqual(len({id(q) for q in results}), 1)

    def test_MD303_stale_venue_quotes_ignored(self):
        now = self.w.clock.time()
        self.w.venues.on_quote(VenueQuote("ARCA", "XYZ", D("101.00"), D("101.05"), now - 21))
        self.w.venues.on_quote(VenueQuote("BATS", "XYZ", D("100.00"), D("100.02"), now - 1))
        body = self.w.api.get_consolidated("XYZ").body
        self.assertEqual((body["bid"], body["ask"]), ("100.00", "100.02"))

    def test_MD304_timestamps_are_utc(self):
        old = os.environ.get("TZ")
        os.environ["TZ"] = "America/New_York"
        time.tzset()
        try:
            self.assertEqual(format_ts(1767225600), "2026-01-01T00:00:00Z")
        finally:
            if old is None:
                del os.environ["TZ"]
            else:
                os.environ["TZ"] = old
            time.tzset()
