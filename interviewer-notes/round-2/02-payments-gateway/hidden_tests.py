import json
import unittest

from gateway.adapters.transport import HttpResult, TransportTimeout
from gateway.adapters.webhooks import sign
from tests.helpers import World, charge_ok


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_pay201_retry_after_timeout_reuses_the_idempotency_key(self):
        self.w.psp.queue(TransportTimeout("read timed out"), charge_ok("ch_1"))
        resp = self.w.pay()
        self.assertEqual(resp.body["status"], "captured")
        keys = [c.headers["Idempotency-Key"] for c in self.w.psp.calls]
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0], keys[1])

    def test_pay205_declines_are_not_retried(self):
        self.w.psp.queue(HttpResult(402, {"error": {"code": "card_declined", "message": "Declined"}}))
        resp = self.w.pay()
        self.assertEqual(len(self.w.psp.calls), 1)
        self.assertEqual(resp.body["status"], "failed")
        self.assertEqual(resp.body["failure_code"], "card_declined")

    def test_pay210_pretty_printed_webhooks_are_accepted(self):
        self.w.psp.queue(charge_ok("ch_42", status="pending"))
        payment = self.w.pay().body
        body = json.dumps({"id": "evt_1", "type": "charge.succeeded", "data": {"id": "ch_42"}}, indent=2).encode()
        ts = int(self.w.clock.now().timestamp())
        tampered = body.replace(b"ch_42", b"ch_43")
        bad = self.w.call("POST", "/webhooks/paystream", headers={"Paystream-Signature": f"t={ts},v1={sign('whsec_test', ts, body)}"},
                          raw=tampered)
        self.assertEqual(bad.status, 401)
        self.assertEqual(self.w.webhook({}, raw=body).status, 200)
        self.assertEqual(self.w.call("GET", f"/payments/{payment['id']}", self.w.bean).body["status"], "captured")

    def test_pay215_zero_and_three_decimal_currencies(self):
        resp = self.w.pay(token=self.w.kyoto, amount="1500", currency="JPY")
        self.assertEqual(self.w.psp.calls[-1].json()["amount"], 1500)
        self.assertEqual(resp.body["amount_minor"], 1500)
        self.assertEqual(resp.body["amount"], "1500")
        self.w.pay(key="kwd", amount="1.250", currency="KWD")
        self.assertEqual(self.w.psp.calls[-1].json()["amount"], 1250)
        self.assertEqual(self.w.pay(key="bad", token=self.w.kyoto, amount="15.5", currency="JPY").status, 400)

    def test_pay220_processor_outage_is_a_retryable_503(self):
        self.w.psp.queue(TransportTimeout("t1"), TransportTimeout("t2"), TransportTimeout("t3"))
        resp = self.w.pay()
        self.assertEqual(resp.status, 503)
        self.assertEqual(str(resp.headers.get("Retry-After")), "30")
        self.assertEqual(resp.body["error"]["code"], "service_unavailable")
        self.assertNotIn("sk_", json.dumps(resp.body))
        items = self.w.call("GET", "/payments", self.w.bean).body["items"]
        self.assertEqual([(p["status"], p["failure_code"]) for p in items], [("failed", "processor_unavailable")])


if __name__ == "__main__":
    unittest.main()
