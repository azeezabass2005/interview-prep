import unittest

from inventory.app import build_app


class TestInventory(unittest.TestCase):
    def test_ship_whole_layer(self):
        api, _ = build_app()
        api.receive("W", "NJ", 100, "2.00", "2026-01-01")
        self.assertEqual(api.ship("S1", "W", "NJ", 100), (201, {"cogs": "200.00"}))


if __name__ == "__main__":
    unittest.main()
