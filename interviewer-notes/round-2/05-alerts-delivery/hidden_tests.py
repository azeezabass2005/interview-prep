import unittest
from datetime import timedelta
from unittest import mock

from alerts.adapters.transport import HttpResult, TransportTimeout
from alerts.clock import iso
from tests.helpers import World


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_alr501_a_job_is_processed_by_one_worker(self):
        self.w.rule(self.w.maya)
        self.w.tick("AAPL", 250)
        queue = self.w.c.queue
        stale = queue.due()
        self.w.worker.run_pending()
        second = self.w.c.worker()
        with mock.patch.object(queue, "due", return_value=stale):
            second.run_pending()
        self.assertEqual(len(self.w.sms.calls), 1)
        job = queue.enqueue("deliver", {"delivery_id": "dlv_missing"})
        self.assertTrue(queue.claim(job))
        self.assertFalse(queue.claim(job))

    def test_alr505_first_retry_after_30_seconds(self):
        self.w.rule(self.w.maya)
        self.w.sms.queue(TransportTimeout("slow"))
        self.w.tick("AAPL", 250)
        self.w.worker.run_pending()
        job = self.w.c.queue.by_status("queued")[0]
        self.assertEqual(job.run_at, iso(self.w.clock.now() + timedelta(seconds=30)))
        self.w.clock.advance(seconds=31)
        self.w.worker.run_pending()
        self.assertEqual(self.w.c.deliveries.for_user("usr_maya")[0].status, "sent")

    def test_alr510_rate_limited_sends_are_retried(self):
        self.w.rule(self.w.maya)
        self.w.sms.queue(HttpResult(429, {"error": "rate limited"}, {"Retry-After": "1"}))
        self.w.tick("AAPL", 250)
        self.w.worker.run_pending()
        self.assertEqual(self.w.c.deliveries.for_user("usr_maya")[0].status, "queued")
        self.w.clock.advance(hours=2)
        self.w.worker.run_pending()
        self.assertEqual(self.w.c.deliveries.for_user("usr_maya")[0].status, "sent")

    def test_alr515_customers_cannot_list_other_customers_rules(self):
        self.w.rule(self.w.omar, symbol="MSFT")
        self.assertEqual(self.w.call("GET", "/rules?user_id=usr_omar", self.w.maya).status, 403)
        resp = self.w.call("GET", "/rules?user_id=usr_omar", self.w.support)
        self.assertEqual([r["symbol"] for r in resp.body["rules"]], ["MSFT"])
        outsider = self.w.c.auth.issue("usr_zed", "org_other", {"user", "support"})
        self.assertEqual(self.w.call("GET", "/rules?user_id=usr_omar", outsider).status, 403)

    def test_alr520_phone_numbers_with_spaces_are_masked(self):
        self.w.rule(self.w.omar)
        self.w.tick("AAPL", 250)
        self.w.worker.run_pending()
        self.assertEqual(self.w.sms.calls[0].json()["to"], "+44 7700 900456")
        logged = str(self.w.c.logger.records)
        self.assertNotIn("900456", logged)
        self.assertNotIn("7700 900", logged)
        self.assertIn("56", self.w.c.logger.events("delivery_sent")[0]["to"])


if __name__ == "__main__":
    unittest.main()
