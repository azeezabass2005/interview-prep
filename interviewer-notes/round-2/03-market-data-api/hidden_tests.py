import unittest

from tests.helpers import World


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_mkt301_limits_are_per_customer_and_plan(self):
        for _ in range(60):
            self.assertEqual(self.w.get("/quotes/AAPL", self.w.basic).status, 200)
        other = self.w.c.auth.issue("usr_cedar", "org_cedar", {"basic"})
        self.assertEqual(self.w.get("/quotes/AAPL", other).status, 200)
        statuses = [self.w.get("/quotes/AAPL", self.w.pro).status for _ in range(100)]
        self.assertEqual(statuses.count(200), 100)
        self.assertEqual(self.w.get("/quotes/AAPL").status, 401)

    def test_mkt305_quotes_expire_after_two_seconds(self):
        self.assertEqual(self.w.get("/quotes/AAPL", self.w.basic).body["price"], 190.0)
        self.w.vendor.prices["AAPL"] = (191.5, "USD")
        self.w.clock.advance(seconds=1)
        self.assertEqual(self.w.get("/quotes/AAPL", self.w.basic).body["price"], 190.0)
        self.w.clock.advance(seconds=2)
        self.assertEqual(self.w.get("/quotes/AAPL", self.w.basic).body["price"], 191.5)

    def test_mkt310_conversion_does_not_change_the_cached_quote(self):
        self.assertEqual(self.w.get("/quotes/AAPL?ccy=EUR", self.w.pro).body["currency"], "EUR")
        plain = self.w.get("/quotes/AAPL", self.w.basic).body
        self.assertEqual((plain["price"], plain["currency"]), (190.0, "USD"))
        gbp = self.w.get("/quotes/AAPL?ccy=GBP", self.w.basic).body
        self.assertEqual((gbp["price"], gbp["currency"]), (152.0, "GBP"))

    def test_mkt315_search_input_is_data_not_sql(self):
        resp = self.w.get("/instruments?q=O'Reilly", self.w.basic)
        self.assertEqual(resp.status, 200)
        self.assertEqual([i["symbol"] for i in resp.body["instruments"]], ["ORLY"])
        resp = self.w.get("/instruments?q=zzz' OR '1'='1", self.w.basic)
        self.assertEqual((resp.status, resp.body["instruments"]), (200, []))

    def test_mkt320_errors_are_counted_and_logged(self):
        self.w.vendor.down = True
        self.assertEqual(self.w.get("/quotes/AAPL", self.w.basic).status, 502)
        self.assertEqual(self.w.get("/quotes/AAPL").status, 401)
        self.assertEqual(self.w.c.metrics.count("http_requests_total", status=502), 1)
        self.assertEqual(self.w.c.metrics.count("http_requests_total", status=401), 1)
        self.assertEqual([r["status"] for r in self.w.c.logger.events("request")], [502, 401])


if __name__ == "__main__":
    unittest.main()
