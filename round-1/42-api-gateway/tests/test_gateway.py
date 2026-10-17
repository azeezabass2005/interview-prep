import unittest
from datetime import datetime

from gateway import Gateway


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestGateway(unittest.TestCase):
    def test_routes_to_backend(self):
        gw = Gateway(Clock(datetime(2026, 5, 4, 12, 0, 10)))
        gw.add_backend("quotes", lambda path: 200)
        gw.add_route("/v1/quotes", "quotes")
        gw.add_key("k1", "FREE")
        self.assertEqual(gw.handle("k1", "10.0.0.1", "/v1/quotes/AAPL"), (200, {}))


if __name__ == "__main__":
    unittest.main()
