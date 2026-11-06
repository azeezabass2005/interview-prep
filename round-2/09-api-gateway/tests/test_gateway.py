import unittest

from edge.adapters.transport import HttpResult, TransportTimeout
from tests.helpers import PARTNER_KEY, World


class RoutingTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_routes_by_prefix(self):
        resp = self.w.call("GET", "/v1/orders/ord_1?fields=status", self.w.alder)
        self.assertEqual(resp.status, 200)
        call = self.w.upstreams.calls[0]
        self.assertEqual(call["url"], "http://orders.internal:8080/orders/ord_1?fields=status")
        self.assertEqual(call["headers"]["X-Client-Id"], "org_alder")

    def test_unknown_route(self):
        self.assertEqual(self.w.call("GET", "/v2/nothing", self.w.alder).status, 404)

    def test_needs_a_token(self):
        self.assertEqual(self.w.call("GET", "/v1/orders").status, 401)
        self.assertEqual(self.w.upstreams.calls, [])

    def test_partner_gets_our_api_key(self):
        self.w.call("GET", "/v1/fx/EURUSD", self.w.alder)
        call = self.w.upstreams.to("api.fxpartner.example")[0]
        self.assertEqual(call["url"], "https://api.fxpartner.example/v2/rates/EURUSD")
        self.assertEqual(call["headers"]["X-Api-Key"], PARTNER_KEY)
        self.assertNotIn("X-Client-Id", call["headers"])

    def test_upstream_status_and_body_pass_through(self):
        self.w.upstreams.queue("orders.internal", HttpResult(409, {"error": "duplicate order"}))
        resp = self.w.call("POST", "/v1/orders", self.w.alder, {"symbol": "AAPL", "qty": 10})
        self.assertEqual((resp.status, resp.body), (409, {"error": "duplicate order"}))

    def test_request_id_is_returned(self):
        resp = self.w.call("GET", "/v1/quotes/AAPL", self.w.alder, headers={"X-Request-ID": "req_abc"})
        self.assertEqual(resp.headers["X-Request-ID"], "req_abc")


class ResilienceTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_get_is_retried_on_503(self):
        self.w.upstreams.queue("quotes.internal", HttpResult(503, {}), HttpResult(200, {"price": 190}))
        resp = self.w.call("GET", "/v1/quotes/AAPL", self.w.alder)
        self.assertEqual((resp.status, resp.body), (200, {"price": 190}))
        self.assertEqual(len(self.w.upstreams.calls), 2)

    def test_upstream_down_is_a_502(self):
        self.w.upstreams.queue("quotes.internal", *[TransportTimeout("slow")] * 3)
        self.assertEqual(self.w.call("GET", "/v1/quotes/AAPL", self.w.alder).status, 502)

    def test_circuit_opens_after_five_failed_requests_and_recovers(self):
        self.w.upstreams.queue("quotes.internal", *[HttpResult(503, {})] * 15)
        for _ in range(5):
            self.assertEqual(self.w.call("GET", "/v1/quotes/AAPL", self.w.alder).status, 502)
        self.assertEqual(self.w.breaker("quotes").state, "open")
        before = len(self.w.upstreams.calls)
        resp = self.w.call("GET", "/v1/quotes/AAPL", self.w.alder)
        self.assertEqual((resp.status, len(self.w.upstreams.calls)), (503, before))
        self.w.clock.advance(seconds=30)
        self.assertEqual(self.w.call("GET", "/v1/quotes/AAPL", self.w.alder).status, 200)
        self.assertEqual(self.w.breaker("quotes").state, "closed")

    def test_breakers_are_per_upstream(self):
        self.w.upstreams.queue("quotes.internal", *[HttpResult(503, {})] * 15)
        for _ in range(5):
            self.w.call("GET", "/v1/quotes/AAPL", self.w.alder)
        self.assertEqual(self.w.call("GET", "/v1/orders/ord_1", self.w.alder).status, 200)

    def test_ops_can_see_breakers(self):
        self.w.call("GET", "/v1/orders/ord_1", self.w.alder)
        self.assertEqual(self.w.call("GET", "/internal/upstreams", self.w.alder).status, 403)
        self.assertEqual(self.w.call("GET", "/internal/upstreams", self.w.ops).body["orders"]["state"], "closed")


class RateLimitTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_100_requests_a_minute_per_client(self):
        statuses = [self.w.call("GET", "/v1/quotes/AAPL", self.w.alder).status for _ in range(101)]
        self.assertEqual(statuses.count(200), 100)
        self.assertEqual(statuses[-1], 429)
        self.assertEqual(self.w.call("GET", "/v1/quotes/AAPL", self.w.birch).status, 200)

    def test_window_slides(self):
        for _ in range(100):
            self.w.call("GET", "/v1/quotes/AAPL", self.w.alder)
        self.w.clock.advance(seconds=60)
        self.assertEqual(self.w.call("GET", "/v1/quotes/AAPL", self.w.alder).status, 200)


if __name__ == "__main__":
    unittest.main()
