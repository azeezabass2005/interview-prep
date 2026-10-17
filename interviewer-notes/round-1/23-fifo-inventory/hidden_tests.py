import unittest
from datetime import date
from decimal import Decimal

from inventory import Inventory

JAN, FEB, MAR, APR = date(2026, 1, 5), date(2026, 2, 5), date(2026, 3, 5), date(2026, 4, 5)


class HiddenInventory(unittest.TestCase):
    def test_B1_oldest_lot_first(self):
        inv = Inventory()
        inv.receive("W1", "X", 5, "10", JAN)
        inv.receive("W1", "X", 5, "12", FEB)
        self.assertEqual(inv.ship("s1", "W1", "X", 3), Decimal("30"))

    def test_B2_all_or_nothing(self):
        inv = Inventory()
        inv.receive("W1", "X", 5, "10", JAN)
        with self.assertRaises(Exception):
            inv.ship("s1", "W1", "X", 8)
        self.assertEqual(inv.on_hand("W1", "X"), 5)

    def test_B3_transfer_keeps_received_date(self):
        inv = Inventory()
        inv.receive("A", "X", 5, "10", JAN)
        inv.receive("B", "X", 5, "12", FEB)
        inv.transfer("A", "B", "X", 2, MAR)
        self.assertEqual([l.received for l in inv.lots("B", "X")], [JAN, FEB])

    def test_B4_return_at_shipment_cost(self):
        inv = Inventory()
        inv.receive("W1", "X", 5, "10", JAN)
        inv.ship("s1", "W1", "X", 2)
        inv.receive("W1", "X", 5, "15", FEB)
        inv.return_goods("s1", 1, MAR)
        self.assertEqual(inv.value("W1", "X"), Decimal("115"))

    def test_B5_reorder_at_the_point(self):
        inv = Inventory()
        inv.set_reorder_point("W1", "X", 3)
        inv.receive("W1", "X", 5, "10", JAN)
        inv.ship("s1", "W1", "X", 2)
        self.assertEqual(inv.reorders, [("W1", "X")])
