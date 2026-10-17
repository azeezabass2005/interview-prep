import unittest
from decimal import Decimal

from oms import OrderManager


class HiddenOms(unittest.TestCase):
    def test_B1_max_quantity_allowed(self):
        self.assertEqual(OrderManager().submit("o1", "acc", "ABC", "BUY", 1_000_000, "0.50").status, "NEW")

    def test_B2_duplicate_exec_ignored(self):
        oms = OrderManager()
        oms.submit("o1", "acc", "ABC", "BUY", 100, "10.00")
        oms.execute("e1", "o1", 50, "10.00")
        self.assertEqual(oms.execute("e1", "o1", 50, "10.00").filled, 50)

    def test_B3_partial_fill_status(self):
        oms = OrderManager()
        oms.submit("o1", "acc", "ABC", "BUY", 100, "10.00")
        self.assertEqual(oms.execute("e1", "o1", 40, "10.00").status, "PARTIALLY_FILLED")

    def test_B4_average_is_quantity_weighted(self):
        oms = OrderManager()
        oms.submit("o1", "acc", "ABC", "BUY", 400, "11.00")
        oms.execute("e1", "o1", 100, "10.00")
        self.assertEqual(oms.execute("e2", "o1", 300, "11.00").avg_price, Decimal("10.7500"))

    def test_B5_sells_reduce_position(self):
        oms = OrderManager()
        oms.submit("o1", "acc", "ABC", "SELL", 100, "10.00")
        oms.execute("e1", "o1", 100, "10.00")
        self.assertEqual(oms.position("acc", "ABC"), -100)
