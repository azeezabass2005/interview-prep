import unittest

from tests.helpers import World


class QuotesTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_latest_quote(self):
        resp = self.w.get("/quotes/aapl", self.w.basic)
        self.assertEqual(resp.status, 200)
        self.assertEqual((resp.body["symbol"], resp.body["price"], resp.body["currency"]), ("AAPL", 190.0, "USD"))

    def test_quote_in_another_currency(self):
        resp = self.w.get("/quotes/AAPL?ccy=EUR", self.w.basic)
        self.assertEqual((resp.body["price"], resp.body["currency"]), (171.0, "EUR"))

    def test_quotes_are_cached_briefly(self):
        self.w.get("/quotes/AAPL", self.w.basic)
        self.w.get("/quotes/AAPL", self.w.basic)
        self.assertEqual(len(self.w.vendor.quote_calls()), 1)

    def test_batch_fetches_only_missing_symbols(self):
        self.w.get("/quotes/AAPL", self.w.basic)
        resp = self.w.get("/quotes?symbols=AAPL,MSFT", self.w.basic)
        self.assertEqual([q["symbol"] for q in resp.body["quotes"]], ["AAPL", "MSFT"])
        self.assertIn("symbols=MSFT", self.w.vendor.quote_calls()[-1])

    def test_unknown_symbol(self):
        self.assertEqual(self.w.get("/quotes/NOPE", self.w.basic).status, 404)

    def test_vendor_outage_is_a_502(self):
        self.w.vendor.down = True
        resp = self.w.get("/quotes/AAPL", self.w.basic)
        self.assertEqual(resp.status, 502)
        self.assertEqual(resp.body["error"]["code"], "upstream_error")

    def test_search(self):
        resp = self.w.get("/instruments?q=micro", self.w.basic)
        self.assertEqual([i["symbol"] for i in resp.body["instruments"]], ["MSFT"])
        self.assertEqual(self.w.get("/instruments?q=s", self.w.basic).status, 400)

    def test_history(self):
        resp = self.w.get("/instruments/AAPL/history?from=2026-05-01&to=2026-05-31", self.w.basic)
        self.assertEqual([b["close"] for b in resp.body["bars"]], [190, 192])
        self.assertEqual(self.w.get("/instruments/AAPL/history?from=2026-05-31&to=2026-05-01", self.w.basic).status, 400)


class PlatformTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_needs_a_token(self):
        self.assertEqual(self.w.get("/quotes/AAPL").status, 401)

    def test_basic_plan_is_limited_to_60_a_minute(self):
        statuses = [self.w.get("/quotes/AAPL", self.w.basic).status for _ in range(61)]
        self.assertEqual(statuses.count(200), 60)
        self.assertEqual(statuses[-1], 429)

    def test_limit_resets_next_minute(self):
        for _ in range(61):
            self.w.get("/quotes/AAPL", self.w.basic)
        self.w.clock.advance(seconds=60)
        self.assertEqual(self.w.get("/quotes/AAPL", self.w.basic).status, 200)

    def test_successful_requests_are_counted(self):
        self.w.get("/quotes/AAPL", self.w.basic)
        self.assertEqual(self.w.c.metrics.count("http_requests_total", status=200), 1)

    def test_metrics_endpoint_is_ops_only(self):
        self.assertEqual(self.w.get("/internal/metrics", self.w.basic).status, 403)
        self.assertEqual(self.w.get("/internal/metrics", self.w.ops).status, 200)


if __name__ == "__main__":
    unittest.main()
