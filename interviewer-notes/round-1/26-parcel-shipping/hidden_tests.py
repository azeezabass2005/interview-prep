import unittest
from decimal import Decimal as D

from ship.parcel import billable_weight
from ship.quote import order_shipping, package_cost
from tests.helpers import box


class HiddenShipping(unittest.TestCase):
    def test_B1_dimensions_rounded_up_first(self):
        self.assertEqual(billable_weight(box("9.1", 10, 10, 1)), 8)

    def test_B2_weight_always_rounds_up(self):
        self.assertEqual(billable_weight(box(6, 6, 6, "6.2")), 7)

    def test_B3_no_fuel_on_residential_fee(self):
        self.assertEqual(package_cost(box(12, 10, 8, "6.2"), 5, residential=True), D("21.97"))

    def test_B4_exactly_48_inches_not_oversize(self):
        self.assertEqual(package_cost(box(48, 2, 2, 1), 1, residential=False), D("6.16"))

    def test_B5_free_shipping_uses_discounted_subtotal(self):
        self.assertGreater(order_shipping([box(6, 6, 6, 3)], 2, False, D("80"), D("10")), 0)

    def test_G1_free_shipping_only_zones_one_to_four(self):
        self.assertGreater(order_shipping([box(6, 6, 6, 3)], 6, False, D("120")), 0)
