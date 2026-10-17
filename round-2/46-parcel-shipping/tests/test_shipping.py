import unittest

from shipping.app import build_app


class TestShipping(unittest.TestCase):
    def test_small_box_commercial(self):
        status, q = build_app().quote({"packages": [{"l": 6, "w": 6, "h": 6, "lb": 3}], "zone": 1, "residential": False,
                                       "subtotal": "20", "ordered_at": "2026-03-03T10:00"})
        self.assertEqual(status, 200)
        self.assertEqual(q["rates"]["SPEEDY"], "6.72")


if __name__ == "__main__":
    unittest.main()
