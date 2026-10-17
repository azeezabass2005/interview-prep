import unittest
from datetime import date
from decimal import Decimal

from inventory import Inventory


class TestInventory(unittest.TestCase):
    def test_ship_from_single_lot(self):
        inv = Inventory()
        inv.receive("W1", "X", 10, "4.00", date(2026, 3, 1))
        self.assertEqual(inv.ship("s1", "W1", "X", 4), Decimal("16.00"))
        self.assertEqual(inv.on_hand("W1", "X"), 6)


if __name__ == "__main__":
    unittest.main()
