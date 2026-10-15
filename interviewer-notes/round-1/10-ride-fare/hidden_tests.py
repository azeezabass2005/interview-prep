import unittest
from datetime import datetime, timedelta
from decimal import Decimal as D

from fare.calculator import FareCalculator
from fare.cancellation import cancellation_fee
from fare.models import Trip
from fare.surge import SurgeFeed


def trip(miles="10", seconds=1200, surge="1.0", tolls="0"):
    return Trip("t1", "midtown", D(miles), seconds, D(surge), D(tolls))


def calc_with_live(zone_surge="1.0"):
    return FareCalculator(SurgeFeed({"midtown": D(zone_surge)}))


class HiddenFare(unittest.TestCase):
    def test_B1_started_minute_counts(self):
        self.assertEqual(calc_with_live().fare_for(trip("5.3", 860)), D("15.36"))

    def test_B2_booking_fee_not_surged(self):
        self.assertEqual(calc_with_live("2.0").fare_for(trip(surge="2.0")), D("43.00"))

    def test_B3_quoted_surge_is_locked(self):
        self.assertEqual(calc_with_live("2.0").fare_for(trip(surge="1.0")), D("22.50"))

    def test_B4_surge_capped(self):
        self.assertEqual(calc_with_live("4.0").fare_for(trip(surge="4.0")), D("63.50"))

    def test_B5_tolls_after_minimum(self):
        self.assertEqual(calc_with_live().fare_for(trip("0.5", 120, tolls="5.00")), D("12.00"))

    def test_G1_late_driver_waives_fee(self):
        t0 = datetime(2026, 5, 1, 18, 0)
        self.assertEqual(cancellation_fee(t0, 300, t0 + timedelta(minutes=12)), D("0.00"))
