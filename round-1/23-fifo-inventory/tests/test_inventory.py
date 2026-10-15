import unittest
from datetime import date
from decimal import Decimal as D

from inventory.ledger import Inventory
from inventory.models import InsufficientStock

JAN1, JAN5, JAN9 = date(2026, 1, 1), date(2026, 1, 5), date(2026, 1, 9)


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()

    def test_receive_and_on_hand(self):
        self.inv.receive("WIDGET", 100, "2.00", JAN1)
        self.inv.receive("WIDGET", 50, "2.50", JAN5)
        self.assertEqual(self.inv.on_hand("WIDGET"), 150)
        self.assertEqual(self.inv.valuation("WIDGET"), D("325.00"))

    def test_ship_whole_layer(self):
        self.inv.receive("WIDGET", 100, "2.00", JAN1)
        self.assertEqual(self.inv.ship("S1", "WIDGET", 100).cogs, D("200.00"))
        self.assertEqual(self.inv.on_hand("WIDGET"), 0)

    def test_cannot_oversell(self):
        self.inv.receive("WIDGET", 10, "2.00", JAN1)
        with self.assertRaises(InsufficientStock):
            self.inv.ship("S1", "WIDGET", 11)

    def test_cannot_return_more_than_shipped(self):
        self.inv.receive("WIDGET", 10, "2.00", JAN1)
        self.inv.ship("S1", "WIDGET", 10)
        with self.assertRaises(ValueError):
            self.inv.return_units("S1", 11, JAN9)


if __name__ == "__main__":
    unittest.main()
