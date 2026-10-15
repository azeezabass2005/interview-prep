import threading
import unittest
from datetime import datetime, timezone
from unittest import mock

from alerts.repositories.deliveries import DeliveryRepository
from alerts.services.alert_service import AlertService
from tests.helpers import World


class HiddenAlerts(unittest.TestCase):
    def tearDown(self):
        self.w.cleanup()

    def test_ALR401_edge_triggered_with_rearm(self):
        self.w = World()
        self.w.api.post_alert("u1", {"symbol": "IBM", "direction": "ABOVE", "threshold": "200"})
        for price in ("200.10", "200.40", "200.20", "199.95", "200.30"):
            self.w.evaluator.on_tick("IBM", price)
        self.assertEqual(len(self.w.deliveries.all()), 1)
        self.w.evaluator.on_tick("IBM", "198.00")
        self.w.evaluator.on_tick("IBM", "200.50")
        self.assertEqual(len(self.w.deliveries.all()), 2)

    def test_ALR402_quiet_hours_span_midnight(self):
        self.w = World(now=datetime(2026, 5, 12, 6, 0, tzinfo=timezone.utc))  # 02:00 in New York
        self.w.api.post_alert("u1", {"symbol": "IBM", "direction": "ABOVE", "threshold": "200"})
        self.w.evaluator.on_tick("IBM", "201")
        self.assertEqual(self.w.deliveries.all()[0].deliver_after, datetime(2026, 5, 12, 11, 0, tzinfo=timezone.utc))

    def test_ALR403_each_delivery_sent_once(self):
        self.w = World()
        self.w.api.post_alert("u1", {"symbol": "IBM", "direction": "ABOVE", "threshold": "200"})
        self.w.evaluator.on_tick("IBM", "201")
        barrier = threading.Barrier(2, timeout=3)
        original = DeliveryRepository.pending_due
        calls = {"n": 0}
        lock = threading.Lock()

        def paused(repo, now, limit):
            result = original(repo, now, limit)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        with mock.patch.object(DeliveryRepository, "pending_due", paused):
            threads = [threading.Thread(target=self.w.worker(f"w{i}").run_once) for i in range(2)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(len(self.w.sender.sent), 1)

    def test_ALR404_deleted_alert_never_fires(self):
        self.w = World()
        alert_id = self.w.api.post_alert("u1", {"symbol": "IBM", "direction": "ABOVE", "threshold": "200"}).body["alert_id"]
        self.w.evaluator.on_tick("IBM", "150")  # evaluator has loaded its index
        AlertService(self.w.db, self.w.clock).delete_alert("u1", alert_id)  # API instance, another process
        self.w.evaluator.on_tick("IBM", "201")
        self.assertEqual(self.w.deliveries.all(), [])
