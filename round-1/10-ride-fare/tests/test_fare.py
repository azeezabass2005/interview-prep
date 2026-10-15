import unittest
from datetime import datetime, timedelta
from decimal import Decimal as D

from fare.calculator import FareCalculator, metered_subtotal
from fare.cancellation import cancellation_fee
from fare.models import Trip
from fare.surge import SurgeFeed


def trip(miles="10", seconds=1200, surge="1.0", tolls="0"):
    return Trip("t1", "midtown", D(miles), seconds, D(surge), D(tolls))


class TestFare(unittest.TestCase):
    def setUp(self):
        self.calc = FareCalculator(SurgeFeed())

    def test_metered_subtotal_whole_minutes(self):
        self.assertEqual(metered_subtotal(trip()), D("20.50"))

    def test_no_surge_fare(self):
        self.assertEqual(self.calc.fare_for(trip()), D("22.50"))

    def test_minimum_fare(self):
        self.assertEqual(self.calc.fare_for(trip(miles="0.5", seconds=120)), D("7.00"))

    def test_distance_rounded_to_hundredth(self):
        self.assertEqual(metered_subtotal(trip(miles="1.004", seconds=60)), D("4.00"))


class TestCancellation(unittest.TestCase):
    T0 = datetime(2026, 5, 1, 18, 0)

    def test_free_within_two_minutes(self):
        self.assertEqual(cancellation_fee(self.T0, 300, self.T0 + timedelta(seconds=90)), D("0.00"))

    def test_fee_after_two_minutes(self):
        self.assertEqual(cancellation_fee(self.T0, 600, self.T0 + timedelta(minutes=4)), D("5.00"))


if __name__ == "__main__":
    unittest.main()
