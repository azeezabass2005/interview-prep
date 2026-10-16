import unittest
from datetime import datetime, timezone

from alerts.models import User
from alerts.services.quiet_hours import in_quiet_hours
from tests.helpers import World


class TestApi(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_create_and_list(self):
        self.assertEqual(self.w.api.post_alert("u1", {"symbol": "ibm", "direction": "ABOVE", "threshold": "200"}).status, 201)
        self.assertEqual(self.w.api.get_alerts("u1").body["alerts"][0]["symbol"], "IBM")

    def test_validation(self):
        self.assertEqual(self.w.api.post_alert("u1", {"symbol": "IBM", "direction": "UP", "threshold": "1"}).status, 400)

    def test_delete_hides_alert(self):
        alert_id = self.w.api.post_alert("u1", {"symbol": "IBM", "direction": "ABOVE", "threshold": "200"}).body["alert_id"]
        self.assertEqual(self.w.api.delete_alert("u1", alert_id).status, 204)
        self.assertEqual(self.w.api.get_alerts("u1").body["alerts"], [])

    def test_cannot_delete_someone_elses_alert(self):
        alert_id = self.w.api.post_alert("u1", {"symbol": "IBM", "direction": "ABOVE", "threshold": "200"}).body["alert_id"]
        self.assertEqual(self.w.api.delete_alert("u2", alert_id).status, 404)


class TestEvaluationAndDelivery(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.api.post_alert("u1", {"symbol": "IBM", "direction": "ABOVE", "threshold": "200"})

    def tearDown(self):
        self.w.cleanup()

    def test_below_threshold_does_nothing(self):
        self.assertEqual(self.w.evaluator.on_tick("IBM", "199.00"), 0)

    def test_reaching_threshold_enqueues_and_worker_sends(self):
        self.w.evaluator.on_tick("IBM", "200.10")
        self.assertEqual(self.w.worker().run_once(), 1)
        self.assertEqual(len(self.w.sender.sent), 1)
        self.assertEqual(self.w.deliveries.all()[0].status, "SENT")

    def test_below_alert(self):
        self.w.api.post_alert("u1", {"symbol": "MSFT", "direction": "BELOW", "threshold": "400"})
        self.assertEqual(self.w.evaluator.on_tick("MSFT", "399.50"), 1)


class TestQuietHours(unittest.TestCase):
    def test_daytime_window(self):
        user = User("u", "America/New_York", "13:00", "14:00")
        self.assertTrue(in_quiet_hours(user, datetime(2026, 5, 12, 17, 30, tzinfo=timezone.utc)))
        self.assertFalse(in_quiet_hours(user, datetime(2026, 5, 12, 19, 0, tzinfo=timezone.utc)))


if __name__ == "__main__":
    unittest.main()
