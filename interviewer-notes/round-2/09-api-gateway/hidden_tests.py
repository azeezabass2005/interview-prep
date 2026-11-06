import unittest

from edge.adapters.transport import HttpResult
from tests.helpers import World


def fail_requests(w, n):
    w.upstreams.queue("quotes.internal", *[HttpResult(503, {})] * (3 * n))
    for _ in range(n):
        w.call("GET", "/v1/quotes/AAPL", w.alder)


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_edge901_only_consecutive_failures_open_the_breaker(self):
        fail_requests(self.w, 4)
        self.assertEqual(self.w.call("GET", "/v1/quotes/AAPL", self.w.alder).status, 200)
        fail_requests(self.w, 4)
        self.assertEqual(self.w.breaker("quotes").state, "closed")
        fail_requests(self.w, 1)
        self.w.clock.advance(seconds=30)
        self.assertEqual(self.w.call("GET", "/v1/quotes/AAPL", self.w.alder).status, 200)
        fail_requests(self.w, 1)
        self.assertEqual(self.w.breaker("quotes").state, "closed")
        before = len(self.w.upstreams.calls)
        self.w.call("GET", "/v1/quotes/AAPL", self.w.alder)
        self.assertEqual(len(self.w.upstreams.calls), before + 1)

    def test_edge905_request_id_reaches_upstreams(self):
        self.w.call("GET", "/v1/orders/ord_1", self.w.alder, headers={"X-Request-ID": "req_trace"})
        self.assertEqual(self.w.upstreams.calls[-1]["headers"].get("X-Request-ID"), "req_trace")
        resp = self.w.call("GET", "/v1/orders/ord_2", self.w.alder)
        self.assertEqual(self.w.upstreams.calls[-1]["headers"].get("X-Request-ID"), resp.headers["X-Request-ID"])

    def test_edge910_client_tokens_never_reach_the_partner(self):
        self.assertEqual(self.w.call("GET", "/v1/fx/EURUSD", self.w.alder).status, 200)
        call = self.w.upstreams.to("api.fxpartner.example")[0]
        self.assertNotIn("Authorization", call["headers"])
        self.assertNotIn(self.w.alder, str(call["headers"]))
        self.assertEqual(call["headers"]["X-Api-Key"], "fxp_live_secret")

    def test_edge915_busy_client_keeps_getting_its_quota(self):
        ok_last_minute = 0
        for i in range(360):  # two requests a second for three minutes
            status = self.w.call("GET", "/v1/quotes/AAPL", self.w.alder).status
            if i >= 240 and status == 200:
                ok_last_minute += 1
            self.w.clock.advance(seconds=0.5)
        self.assertGreaterEqual(ok_last_minute, 90)

    def test_edge920_unsafe_requests_are_not_retried(self):
        self.w.upstreams.queue("orders.internal", HttpResult(503, {}), HttpResult(201, {"id": "ord_9"}))
        resp = self.w.call("POST", "/v1/orders", self.w.alder, {"symbol": "AAPL", "qty": 10})
        self.assertEqual(len(self.w.upstreams.to("orders.internal")), 1)
        self.assertEqual(resp.status, 502)
        self.w.upstreams.scripts.clear()
        self.w.upstreams.queue("orders.internal", HttpResult(503, {}), HttpResult(201, {"id": "ord_10"}))
        resp = self.w.call("POST", "/v1/orders", self.w.alder, {"symbol": "AAPL", "qty": 10}, headers={"Idempotency-Key": "k1"})
        self.assertEqual((resp.status, len(self.w.upstreams.to("orders.internal"))), (201, 3))


if __name__ == "__main__":
    unittest.main()
