import unittest

from gateway.adapters.transport import HttpResult
from tests.helpers import World, charge_ok


class PaymentsTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_successful_charge(self):
        resp = self.w.pay()
        self.assertEqual(resp.status, 201)
        self.assertEqual(resp.body["status"], "captured")
        self.assertEqual(resp.body["amount"], "12.50")
        sent = self.w.psp.calls[0].json()
        self.assertEqual((sent["amount"], sent["currency"], sent["source"]), (1250, "usd", "tok_card_visa_4242"))

    def test_idempotent_replay_returns_the_same_payment(self):
        first = self.w.pay(key="order-7")
        second = self.w.pay(key="order-7")
        self.assertEqual(second.status, 200)
        self.assertEqual(first.body["id"], second.body["id"])
        self.assertEqual(len(self.w.psp.calls), 1)

    def test_payments_are_scoped_to_the_merchant(self):
        payment = self.w.pay().body
        self.assertEqual(self.w.call("GET", f"/payments/{payment['id']}", self.w.bean).status, 200)
        self.assertEqual(self.w.call("GET", f"/payments/{payment['id']}", self.w.kyoto).status, 404)

    def test_pending_charge_waits_for_webhook(self):
        self.w.psp.queue(charge_ok("ch_9", status="pending"))
        self.assertEqual(self.w.pay().body["status"], "pending")

    def test_declined_card_fails_the_payment(self):
        self.w.psp.queue(*[HttpResult(402, {"error": {"code": "card_declined", "message": "Declined"}})] * 3)
        resp = self.w.pay()
        self.assertEqual(resp.status, 201)
        self.assertEqual(resp.body["status"], "failed")

    def test_validation(self):
        self.assertEqual(self.w.pay(currency="XYZ").status, 400)
        self.assertEqual(self.w.pay(amount="1.234").status, 400)
        self.assertEqual(self.w.pay(amount="-5").status, 400)
        self.assertEqual(self.w.pay(card="4242424242424242").status, 400)
        resp = self.w.call("POST", "/payments", self.w.bean, {"amount": "1.00", "currency": "USD", "card_token": "tok_card_x"})
        self.assertEqual(resp.status, 400)

    def test_list_by_status(self):
        self.w.pay(key="a")
        self.w.psp.queue(*[HttpResult(402, {"error": {"code": "card_declined"}})] * 3)
        self.w.pay(key="b")
        failed = self.w.call("GET", "/payments?status=failed", self.w.bean).body["items"]
        self.assertEqual(len(failed), 1)

    def test_partial_and_over_refunds(self):
        payment = self.w.pay(amount="10.00").body
        self.w.psp.queue(HttpResult(200, {"id": "re_1", "status": "succeeded"}))
        self.assertEqual(self.w.call("POST", f"/payments/{payment['id']}/refunds", self.w.bean, {"amount": "4.00"}).status, 201)
        over = self.w.call("POST", f"/payments/{payment['id']}/refunds", self.w.bean, {"amount": "6.01"})
        self.assertEqual(over.status, 400)
        self.assertEqual(len(self.w.call("GET", f"/payments/{payment['id']}/refunds", self.w.bean).body["items"]), 1)

    def test_amounts_round_trip_for_two_decimal_currencies(self):
        resp = self.w.pay(amount="0.99", currency="GBP")
        self.assertEqual(resp.body["amount_minor"], 99)
        self.assertEqual(resp.body["amount"], "0.99")


if __name__ == "__main__":
    unittest.main()
