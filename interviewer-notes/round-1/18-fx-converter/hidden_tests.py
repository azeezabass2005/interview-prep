import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from fx import FxDesk

T0 = datetime(2026, 7, 1, 12, 0, 0)


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


def desk():
    clock = Clock(T0)
    d = FxDesk(clock)
    for ccy, rate in (("EUR", "0.92"), ("GBP", "0.80"), ("JPY", "155")):
        d.set_rate(ccy, rate)
    return d, clock


class HiddenFx(unittest.TestCase):
    def test_B1_cross_rate_direction(self):
        d, _ = desk()
        self.assertEqual(round(d.mid("EUR", "GBP"), 6), Decimal("0.869565"))

    def test_B2_spread_against_the_client(self):
        d, _ = desk()
        self.assertEqual(d.quote("acme", "USD", "EUR", 1000)["receive"], Decimal("915.40"))

    def test_B3_jpy_has_no_decimals(self):
        d, _ = desk()
        self.assertEqual(str(d.quote("acme", "USD", "JPY", 100)["receive"]), "15422")

    def test_B4_bookable_at_30_seconds(self):
        d, clock = desk()
        q = d.quote("acme", "USD", "EUR", 100)
        clock.current = T0 + timedelta(seconds=30)
        self.assertEqual(d.book(q["quote_id"])["status"], "BOOKED")

    def test_B5_limit_in_usd_equivalent(self):
        d, _ = desk()
        q = d.quote("acme", "JPY", "USD", 1_000_000)
        self.assertEqual(d.book(q["quote_id"])["status"], "BOOKED")
