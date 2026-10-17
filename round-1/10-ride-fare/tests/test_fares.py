import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from fares import RideService

T0 = datetime(2026, 4, 1, 8, 0)


class TestFares(unittest.TestCase):
    def test_simple_trip_total(self):
        rides = RideService()
        rides.request("t1", "ana", T0)
        rides.accept("t1", "dan", T0)
        rides.arrive("t1", T0 + timedelta(minutes=4))
        rides.start("t1", T0 + timedelta(minutes=5))
        receipt = rides.complete("t1", 10, 20)
        self.assertEqual(receipt["total"], Decimal("22.00"))


if __name__ == "__main__":
    unittest.main()
