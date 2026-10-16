import unittest

from shipping.app import build_app


def q(packages, zone=1, residential=False, subtotal="20", discount="0", at="2026-03-03T10:00"):
    return build_app().quote({"packages": packages, "zone": zone, "residential": residential, "subtotal": subtotal,
                              "discount": discount, "ordered_at": at})[1]


class HiddenShipping(unittest.TestCase):
    def test_B1_dimensions_rounded_up(self):
        self.assertEqual(q([{"l": "11.2", "w": 10, "h": 10, "lb": 1}])["rates"]["SPEEDY"], "10.08")

    def test_B2_weight_rounds_up(self):
        self.assertEqual(q([{"l": 6, "w": 6, "h": 6, "lb": "6.2"}])["rates"]["SPEEDY"], "8.96")

    def test_B3_no_fuel_on_residential(self):
        self.assertEqual(q([{"l": 12, "w": 10, "h": 8, "lb": "6.2"}], zone=5, residential=True)["rates"]["SPEEDY"], "21.97")

    def test_B4_free_shipping_after_discount(self):
        self.assertNotEqual(q([{"l": 6, "w": 6, "h": 6, "lb": 3}], zone=2, subtotal="80", discount="10")["shipping"], "0.00")

    def test_B5_cutoff_inclusive(self):
        result = q([{"l": 6, "w": 6, "h": 6, "lb": 3}], at="2026-03-03T14:00")
        self.assertEqual((result["carrier"], result["delivery"]), ("VALUE", "2026-03-10"))
