import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from fares import RideService

T0 = datetime(2026, 4, 1, 8, 0)


def ride(km, minutes, wait_minutes=1, surge=None, promo=0, surge_later=None):
    rides = RideService()
    if surge:
        rides.set_surge(surge)
    rides.request("t1", "ana", T0, promo)
    if surge_later:
        rides.set_surge(surge_later)
    rides.accept("t1", "dan", T0)
    rides.arrive("t1", T0 + timedelta(minutes=3))
    rides.start("t1", T0 + timedelta(minutes=3 + wait_minutes))
    return rides.complete("t1", km, minutes)


class HiddenFares(unittest.TestCase):
    def test_B1_surge_locked_at_request(self):
        self.assertEqual(ride(10, 20, surge="1.5", surge_later="2.0")["fare"], Decimal("30.75"))

    def test_B2_minimum_after_surge(self):
        self.assertEqual(ride(1, 2, surge="1.2")["fare"], Decimal("7.00"))

    def test_B3_first_two_minutes_free(self):
        self.assertEqual(ride(10, 20, wait_minutes=5)["waiting"], Decimal("1.20"))

    def test_B4_discount_capped(self):
        self.assertEqual(ride(50, 40, promo=20)["discount"], Decimal("10.00"))

    def test_B5_payout_before_promo(self):
        self.assertEqual(ride(50, 40, promo=20)["driver_payout"], Decimal("55.88"))
