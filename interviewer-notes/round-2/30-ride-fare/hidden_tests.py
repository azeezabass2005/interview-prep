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


def trip(surge=None, promo=None, wait=timedelta(0), ride=timedelta(minutes=20), miles="10", tolls="0", surge_change=None):
    clock = FakeClock(datetime(2026, 5, 1, 18, 0))
    api, feed, _ = build_app(clock)
    if surge:
        feed.set("midtown", surge)
    tid = api.request({"rider": "r", "zone": "midtown", "promo": promo})[1]["trip_id"]
    api.assign(tid, "d", 300)
    clock.advance(minutes=3)
    api.arrive(tid)
    clock.current += wait
    api.pick_up(tid)
    if surge_change:
        feed.set("midtown", surge_change)
    clock.current += ride
    return api.complete(tid, {"miles": miles, "tolls": tolls})[1]


class HiddenRides(unittest.TestCase):
    def test_B1_started_minute_counts(self):
        self.assertEqual(trip(miles="5.3", ride=timedelta(minutes=14, seconds=20))["fare"], "15.36")

    def test_B2_locked_surge(self):
        self.assertEqual(trip(surge="1.5", surge_change="2.0")["fare"], "32.75")

    def test_B3_free_wait_minutes_not_charged(self):
        self.assertEqual(trip(wait=timedelta(minutes=5))["fare"], "23.70")

    def test_B4_promo_excludes_tolls(self):
        self.assertEqual(trip(promo="SPRING20", tolls="3.00")["fare"], "21.00")

    def test_B5_driver_payout_excludes_booking_fee(self):
        result = trip(surge="1.5", miles="5.3", ride=timedelta(minutes=14, seconds=20), tolls="3.00")
        self.assertEqual(result["driver_payout"], "18.03")
