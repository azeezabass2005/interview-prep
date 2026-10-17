import unittest
from datetime import datetime, timedelta

from stock import StockService

T0 = datetime(2026, 11, 27, 9, 0)


def service(**stock):
    s = StockService()
    for sku, qty in stock.items():
        s.restock(sku, qty)
    return s


class HiddenStock(unittest.TestCase):
    def test_B1_expired_reservations_free_stock(self):
        s = service(TV=5)
        s.reserve("a", "TV", 5, T0)
        s.reserve("b", "TV", 5, T0 + timedelta(minutes=16))
        self.assertEqual(s.reservations[("b", "TV")].quantity, 5)

    def test_B2_reserving_again_replaces(self):
        s = service(TV=10)
        s.reserve("a", "TV", 3, T0)
        s.reserve("a", "TV", 5, T0)
        self.assertEqual(s.available("TV", T0), 5)

    def test_B3_checkout_all_or_nothing(self):
        s = service(ABC=10, ZED=10)
        s.reserve("a", "ZED", 2, T0)
        s.reserve("a", "ABC", 2, T0 + timedelta(minutes=10))
        with self.assertRaises(Exception):
            s.checkout("a", T0 + timedelta(minutes=16))
        self.assertEqual(s.on_hand["ABC"], 10)

    def test_B4_checkout_removes_reservations(self):
        s = service(TV=10)
        s.reserve("a", "TV", 4, T0)
        s.checkout("a", T0)
        self.assertEqual(s.available("TV", T0), 6)

    def test_B5_one_alert_until_restocked(self):
        s = service(TV=8)
        s.reserve("a", "TV", 3, T0)
        s.reserve("b", "TV", 1, T0)
        self.assertEqual(s.alerts, ["TV"])
