import unittest
from datetime import datetime, timedelta

from rides.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current

    def advance(self, **kw):
        self.current += timedelta(**kw)


class TestRides(unittest.TestCase):
    def test_simple_trip(self):
        clock = FakeClock(datetime(2026, 5, 1, 18, 0))
        api, surge, _ = build_app(clock)
        trip = api.request({"rider": "r1", "zone": "midtown"})[1]["trip_id"]
        api.assign(trip, "d1", 300)
        clock.advance(minutes=4)
        api.arrive(trip)
        api.pick_up(trip)
        clock.advance(minutes=20)
        self.assertEqual(api.complete(trip, {"miles": "10"})[1]["fare"], "22.50")


if __name__ == "__main__":
    unittest.main()
