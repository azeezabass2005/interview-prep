import unittest

from alerts.adapters.transport import HttpResult, TransportTimeout
from tests.helpers import World


class RulesTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_create_and_list_own_rules(self):
        self.assertEqual(self.w.rule(self.w.maya).status, 201)
        self.w.rule(self.w.omar, symbol="MSFT")
        rules = self.w.call("GET", "/rules", self.w.maya).body["rules"]
        self.assertEqual([r["symbol"] for r in rules], ["AAPL"])

    def test_validation(self):
        self.assertEqual(self.w.rule(self.w.maya, direction="sideways").status, 400)
        self.assertEqual(self.w.rule(self.w.maya, threshold="lots").status, 400)
        self.assertEqual(self.w.rule(self.w.maya, channel="pigeon").status, 400)

    def test_cannot_delete_someone_elses_rule(self):
        rule = self.w.rule(self.w.omar).body
        self.assertEqual(self.w.call("DELETE", f"/rules/{rule['id']}", self.w.maya).status, 404)
        self.assertEqual(self.w.call("DELETE", f"/rules/{rule['id']}", self.w.omar).status, 204)

    def test_only_the_feed_can_post_prices(self):
        self.assertEqual(self.w.call("POST", "/internal/prices", self.w.maya, {"symbol": "AAPL", "price": 1}).status, 403)


class DeliveryTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_crossing_the_threshold_sends_one_sms(self):
        self.w.rule(self.w.maya, threshold=200)
        self.assertEqual(self.w.tick("AAPL", 199.5).body["fired"], 0)
        self.assertEqual(self.w.tick("AAPL", 200.1).body["fired"], 1)
        self.assertEqual(self.w.tick("AAPL", 201).body["fired"], 0)
        self.assertEqual(self.w.worker.run_pending(), 1)
        self.assertEqual(len(self.w.sms.calls), 1)
        self.assertEqual(self.w.sms.calls[0].json()["to"], "+447700900123")
        self.assertEqual(self.w.call("GET", "/deliveries", self.w.maya).body["deliveries"][0]["status"], "sent")

    def test_email_alerts(self):
        self.w.rule(self.w.maya, direction="below", threshold=100, channel="email")
        self.w.tick("AAPL", 99)
        self.w.worker.run_pending()
        self.assertEqual(self.w.email.calls[0].json()["to"], "maya.lee@example.com")

    def test_transient_failure_is_retried(self):
        self.w.rule(self.w.maya)
        self.w.sms.queue(TransportTimeout("slow"))
        self.w.tick("AAPL", 250)
        self.w.worker.run_pending()
        self.assertEqual(self.w.c.queue.by_status("queued")[0].attempts, 1)
        self.w.clock.advance(hours=2)
        self.w.worker.run_pending()
        self.assertEqual(len(self.w.sms.calls), 2)
        self.assertEqual(self.w.c.deliveries.for_user("usr_maya")[0].status, "sent")

    def test_invalid_number_is_not_retried(self):
        self.w.rule(self.w.maya)
        self.w.sms.queue(HttpResult(400, {"error": "invalid 'to' number"}))
        self.w.tick("AAPL", 250)
        self.w.worker.run_pending()
        self.assertEqual(self.w.c.deliveries.for_user("usr_maya")[0].status, "failed")
        self.assertEqual(self.w.c.queue.by_status("queued"), [])

    def test_gives_up_after_five_attempts(self):
        self.w.rule(self.w.maya)
        self.w.sms.queue(*[HttpResult(503, {})] * 5)
        self.w.tick("AAPL", 250)
        for _ in range(6):
            self.w.worker.run_pending()
            self.w.clock.advance(hours=2)
        self.assertEqual(len(self.w.sms.calls), 5)
        self.assertEqual(len(self.w.c.queue.by_status("dead")), 1)

    def test_logs_mask_contact_details(self):
        self.w.rule(self.w.maya)
        self.w.rule(self.w.maya, symbol="MSFT", channel="email")
        self.w.tick("AAPL", 250)
        self.w.tick("MSFT", 999)
        self.w.worker.run_pending()
        logged = str(self.w.c.logger.records)
        self.assertNotIn("7700900123", logged)
        self.assertNotIn("maya.lee@", logged)
