import unittest
from datetime import timedelta

from tests.helpers import World, charge_ok


def event(event_id, kind, charge_id, **data):
    return {"id": event_id, "type": kind, "data": {"id": charge_id, **data}}


class WebhooksTest(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.psp.queue(charge_ok("ch_42", status="pending"))
        self.payment = self.w.pay().body

    def tearDown(self):
        self.w.cleanup()

    def status(self):
        return self.w.call("GET", f"/payments/{self.payment['id']}", self.w.bean).body["status"]

    def test_charge_succeeded_captures_the_payment(self):
        self.assertEqual(self.w.webhook(event("evt_1", "charge.succeeded", "ch_42")).status, 200)
        self.assertEqual(self.status(), "captured")

    def test_charge_failed(self):
        self.w.webhook(event("evt_1", "charge.failed", "ch_42", failure_code="insufficient_funds"))
        self.assertEqual(self.status(), "failed")

    def test_redelivered_event_is_applied_once(self):
        self.w.webhook(event("evt_1", "charge.succeeded", "ch_42"))
        self.assertEqual(self.w.webhook(event("evt_1", "charge.succeeded", "ch_42")).status, 200)
        self.assertEqual(len(self.w.c.logger.events("webhook_applied")), 1)

    def test_wrong_secret_is_rejected(self):
        self.assertEqual(self.w.webhook(event("evt_1", "charge.succeeded", "ch_42"), secret="whsec_wrong").status, 401)
        self.assertEqual(self.status(), "pending")

    def test_old_timestamp_is_rejected(self):
        old = self.w.clock.now() - timedelta(minutes=10)
        self.assertEqual(self.w.webhook(event("evt_1", "charge.succeeded", "ch_42"), at=old).status, 401)

    def test_missing_signature(self):
        self.assertEqual(self.w.call("POST", "/webhooks/paystream", raw=b"{}").status, 401)


if __name__ == "__main__":
    unittest.main()
