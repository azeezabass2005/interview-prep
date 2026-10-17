import unittest
from datetime import date
from decimal import Decimal

from statement import Card


class TestStatement(unittest.TestCase):
    def test_first_cycle_has_grace(self):
        card = Card()
        card.purchase(date(2026, 3, 5), "400.00")
        s = card.close(date(2026, 3, 1), date(2026, 3, 30))
        self.assertEqual((s["purchase_interest"], s["balance"]), (Decimal("0.00"), Decimal("400.00")))


if __name__ == "__main__":
    unittest.main()
