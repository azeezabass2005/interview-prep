import threading
import unittest
from unittest import mock

from stock.errors import InsufficientStock
from stock.repositories.skus import SkuRepository
from tests.helpers import World


class HiddenStock(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_INV901_bundle_counts_complete_kits(self):
        self.assertEqual(self.w.api.get_availability("DESKKIT").body["available"], 3)

    def test_INV902_expired_reservation_released_once(self):
        self.w.api.post_reservation("cart1", {"sku": "KB-1", "qty": 3})
        self.w.clock.advance(16)
        svc = self.w.reservation_service()
        for _ in range(3):
            svc.sweep_expired()
        kb = self.w.skus.get("KB-1")
        self.assertEqual((kb.reserved, kb.available), (0, 5))

    def test_INV903_race_for_last_units(self):
        a, b = self.w.reservation_service(), self.w.reservation_service()
        barrier = threading.Barrier(2, timeout=3)
        original = SkuRepository.get
        local = threading.local()

        def paused(repo, sku):
            result = original(repo, sku)
            local.calls = getattr(local, "calls", 0) + 1
            if local.calls == 2:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        outcomes = []

        def run(svc, cart):
            try:
                svc.reserve(cart, "KB-1", 3)
                outcomes.append("ok")
            except InsufficientStock:
                outcomes.append("insufficient")

        with mock.patch.object(SkuRepository, "get", paused):
            threads = [threading.Thread(target=run, args=(a, "c1")), threading.Thread(target=run, args=(b, "c2"))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(sorted(outcomes), ["insufficient", "ok"])
        self.assertEqual(self.w.skus.get("KB-1").reserved, 3)
        self.assertEqual(self.w.reservations.active_total("KB-1"), 3)

    def test_INV904_low_stock_at_or_below_reorder_point(self):
        self.w.skus.add("HUB", "USB hub", 20, reorder_point=20)
        self.w.skus.add("PAD", "Mouse pad", 8, reorder_point=5)
        names = [i["sku"] for i in self.w.api.get_low_stock().body["items"]]
        self.assertIn("HUB", names)
        self.assertNotIn("PAD", names)
