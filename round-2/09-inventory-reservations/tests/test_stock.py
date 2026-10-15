import unittest

from tests.helpers import World


class TestStock(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_reserve_reduces_availability(self):
        self.assertEqual(self.w.api.post_reservation("cart1", {"sku": "KB-1", "qty": 2}).status, 201)
        self.assertEqual(self.w.api.get_availability("KB-1").body["available"], 3)

    def test_insufficient(self):
        self.assertEqual(self.w.api.post_reservation("cart1", {"sku": "KB-1", "qty": 6}).status, 409)

    def test_checkout(self):
        self.w.api.post_reservation("cart1", {"sku": "MOUSE", "qty": 4})
        self.assertEqual(self.w.api.post_checkout("cart1").status, 200)
        mouse = self.w.skus.get("MOUSE")
        self.assertEqual((mouse.on_hand, mouse.reserved), (36, 0))

    def test_bundle_reservation_reserves_components(self):
        self.w.api.post_reservation("cart1", {"sku": "DESKKIT", "qty": 2})
        self.assertEqual(self.w.skus.get("USBC").reserved, 4)
        self.assertEqual(self.w.skus.get("DOCK").reserved, 2)

    def test_sweeper_releases_expired(self):
        self.w.api.post_reservation("cart1", {"sku": "KB-1", "qty": 2})
        self.w.clock.advance(16)
        self.assertEqual(self.w.reservation_service().sweep_expired(), 1)
        self.assertEqual(self.w.api.get_availability("KB-1").body["available"], 5)

    def test_low_stock_report(self):
        names = [i["sku"] for i in self.w.api.get_low_stock().body["items"]]
        self.assertIn("KB-1", names)
        self.assertNotIn("MOUSE", names)


if __name__ == "__main__":
    unittest.main()
