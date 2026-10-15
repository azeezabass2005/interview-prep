import unittest
from decimal import Decimal as D

from mdcache.models import VenueQuote
from tests.helpers import World


class TestQuotes(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_first_request_hits_vendor(self):
        resp = self.w.api.get_quote("IBM")
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.body["last"], "180.00")
        self.assertEqual(self.w.provider.calls, ["IBM"])

    def test_second_request_served_from_cache(self):
        self.w.api.get_quote("IBM")
        self.w.clock.advance(0.5)
        self.w.api.get_quote("IBM")
        self.assertEqual(len(self.w.provider.calls), 1)

    def test_vendor_failure_falls_back_to_close(self):
        self.w.closes.record_close("IBM", "2026-05-29", D("179.10"), self.w.clock.time() - 3600)
        self.w.provider.fail = True
        body = self.w.api.get_quote("IBM").body
        self.assertEqual((body["last"], body["stale"]), ("179.10", True))

    def test_unknown_symbol(self):
        self.w.provider.fail = True
        self.assertEqual(self.w.api.get_quote("ZZZZ").status, 404)

    def test_bad_symbol(self):
        self.assertEqual(self.w.api.get_quote("IB M").status, 400)

    def test_timestamp_format(self):
        self.assertTrue(self.w.api.get_quote("IBM").body["updated_at"].endswith("Z"))


class TestConsolidated(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_best_bid_and_offer_across_fresh_venues(self):
        now = self.w.clock.time()
        self.w.venues.on_quote(VenueQuote("ARCA", "XYZ", D("100.00"), D("100.04"), now - 0.5))
        self.w.venues.on_quote(VenueQuote("BATS", "XYZ", D("100.01"), D("100.03"), now - 0.2))
        body = self.w.api.get_consolidated("xyz").body
        self.assertEqual((body["bid"], body["ask"]), ("100.01", "100.03"))

    def test_no_quotes(self):
        self.assertEqual(self.w.api.get_consolidated("XYZ").status, 404)


if __name__ == "__main__":
    unittest.main()
