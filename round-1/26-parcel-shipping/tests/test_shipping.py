import unittest
from decimal import Decimal as D

from ship.parcel import billable_weight
from ship.quote import order_shipping, package_cost
from tests.helpers import box


class TestWeights(unittest.TestCase):
    def test_actual_weight_dominates(self):
        self.assertEqual(billable_weight(box(6, 6, 6, 10)), 10)

    def test_dim_weight_dominates(self):
        self.assertEqual(billable_weight(box(20, 20, 20, 5)), 58)  # 8000 / 139 = 57.55


class TestCost(unittest.TestCase):
    def test_commercial_zone_one(self):
        self.assertEqual(package_cost(box(6, 6, 6, 3), 1, residential=False), D("6.72"))  # 6.00 + 0.72

    def test_unknown_zone(self):
        with self.assertRaises(ValueError):
            package_cost(box(6, 6, 6, 3), 9, residential=False)

    def test_order_sums_packages(self):
        packages = [box(6, 6, 6, 3), box(6, 6, 6, 3)]
        self.assertEqual(order_shipping(packages, 1, False, D("20")), D("13.44"))

    def test_free_shipping_big_order(self):
        self.assertEqual(order_shipping([box(6, 6, 6, 3)], 2, True, D("120")), D("0.00"))


if __name__ == "__main__":
    unittest.main()
