import unittest
from datetime import date, datetime
from decimal import Decimal

from shipping import Parcel, billable_weight, choose, delivery_date, price

MONDAY = datetime(2026, 3, 2, 10, 0)


class HiddenShipping(unittest.TestCase):
    def test_B1_weight_rounds_up(self):
        self.assertEqual(billable_weight(Parcel(Decimal("2.1"), 10, 10, 10)), Decimal("2.5"))

    def test_B2_no_fuel_on_surcharges(self):
        self.assertEqual(price("SWIFT", Parcel(Decimal("5"), 130, 20, 20), 1), Decimal("46.90"))

    def test_B3_order_at_15_00_ships_same_day(self):
        self.assertEqual(delivery_date("SWIFT", 1, datetime(2026, 3, 2, 15, 0)), date(2026, 3, 3))

    def test_B4_business_days_skip_weekend(self):
        self.assertEqual(delivery_date("BUDGET", 1, datetime(2026, 3, 6, 10, 0)), date(2026, 3, 11))

    def test_B5_free_shipping_only_if_budget_meets_deadline(self):
        choice = choose(Parcel(Decimal("1"), 10, 10, 10), 1, 150, MONDAY, deadline=date(2026, 3, 3))
        self.assertEqual(choice["carrier"], "SWIFT")
