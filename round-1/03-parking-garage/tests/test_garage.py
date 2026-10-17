import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from garage import Garage

T0 = datetime(2026, 5, 4, 9, 0)


class TestGarage(unittest.TestCase):
    def test_one_and_a_half_hours(self):
        g = Garage()
        t = g.enter("AB12", T0)
        self.assertEqual(g.amount_due(t, T0 + timedelta(minutes=90)), Decimal("6.00"))


if __name__ == "__main__":
    unittest.main()
