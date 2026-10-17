import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from garage import Garage, GarageError

T0 = datetime(2026, 5, 4, 9, 0)


class HiddenGarage(unittest.TestCase):
    def test_B1_fifteen_minutes_free(self):
        g = Garage()
        t = g.enter("A", T0)
        self.assertEqual(g.amount_due(t, T0 + timedelta(minutes=15)), Decimal("0.00"))

    def test_B2_validation_reduces_time_not_money(self):
        g = Garage()
        t = g.enter("A", T0)
        g.validate(t)
        self.assertEqual(g.amount_due(t, T0 + timedelta(hours=10)), Decimal("20.00"))

    def test_B3_daily_max_per_24_hours(self):
        g = Garage()
        t = g.enter("A", T0)
        self.assertEqual(g.amount_due(t, T0 + timedelta(hours=26)), Decimal("26.00"))

    def test_B4_one_validation_per_ticket(self):
        g = Garage()
        t = g.enter("A", T0)
        g.validate(t)
        with self.assertRaises(GarageError):
            g.validate(t)

    def test_B5_reserved_spaces(self):
        g = Garage(capacity=10, reserved=2)
        for i in range(8):
            g.enter(f"V{i}", T0)
        with self.assertRaises(GarageError):
            g.enter("V9", T0)
        g.enter("P1", T0, permit=True)
