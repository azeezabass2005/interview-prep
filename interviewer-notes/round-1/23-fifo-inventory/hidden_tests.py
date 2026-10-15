import unittest
from datetime import date
from decimal import Decimal as D

from inventory.ledger import Inventory

JAN1, JAN5, JAN9 = date(2026, 1, 1), date(2026, 1, 5), date(2026, 1, 9)


class HiddenInventory(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()

    def test_B1_oldest_layers_first(self):
        self.inv.receive("W", 100, "2.00", JAN1)
        self.inv.receive("W", 50, "2.50", JAN5)
        self.assertEqual(self.inv.ship("S1", "W", 120).cogs, D("250.00"))

    def test_B2_rejected_shipment_changes_nothing(self):
        self.inv.receive("W", 10, "2.00", JAN1)
        with self.assertRaises(Exception):
            self.inv.ship("S1", "W", 15)
        self.assertEqual(self.inv.on_hand("W"), 10)

    def test_B3_partial_layer_keeps_remainder(self):
        self.inv.receive("W", 100, "2.00", JAN1)
        self.inv.ship("S1", "W", 30)
        self.assertEqual(self.inv.valuation("W"), D("140.00"))

    def test_B4_return_at_shipment_average_cost(self):
        self.inv.receive("W", 100, "2.00", JAN1)
        self.inv.ship("S1", "W", 40)
        self.inv.receive("W", 10, "3.00", JAN5)
        layer = self.inv.return_units("S1", 5, JAN9)
        self.assertEqual(layer.unit_cost, D("2.0000"))

    def test_B5_skus_do_not_share_layers(self):
        self.inv.receive("A", 10, "1.00", JAN1)
        self.inv.receive("B", 10, "5.00", JAN1)
        self.assertEqual(self.inv.ship("S1", "B", 5).cogs, D("25.00"))
        other = Inventory()
        other.receive("B", 10, "5.00", JAN1)
        other.receive("A", 10, "1.00", JAN1)
        self.assertEqual(other.ship("S2", "B", 5).cogs, D("25.00"))
        self.assertEqual(other.on_hand("A"), 10)

    def test_spec_example(self):
        self.inv.receive("W", 100, "2.00", JAN1)
        self.inv.receive("W", 50, "2.50", JAN5)
        self.inv.ship("S1", "W", 120)
        self.inv.return_units("S1", 10, JAN9)
        self.assertEqual(self.inv.valuation("W"), D("95.83"))
