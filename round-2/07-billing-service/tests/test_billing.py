import unittest
from datetime import datetime

from tests.helpers import World


class SeatsTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_adding_seats_on_the_first_charges_a_full_month(self):
        self.w.clock._now = datetime(2026, 6, 1, 9, 0)
        resp = self.w.call("POST", "/seats", self.w.acme, {"seats": 12})
        self.assertEqual(resp.body, {"seats": 12, "prorated_charge_cents": 9_998})

    def test_adding_seats_on_the_last_day_charges_one_day(self):
        self.w.clock._now = datetime(2026, 6, 30, 9, 0)
        resp = self.w.call("POST", "/seats", self.w.acme, {"seats": 13})
        self.assertEqual(resp.body["prorated_charge_cents"], 500)  # 3 × 4,999 × 1/30 = 499.9

    def test_removing_seats_is_free(self):
        self.assertEqual(self.w.call("POST", "/seats", self.w.acme, {"seats": 5}).body["prorated_charge_cents"], 0)

    def test_only_billing_admins_change_seats(self):
        self.assertEqual(self.w.call("POST", "/seats", self.w.acme_viewer, {"seats": 11}).status, 403)
        self.assertEqual(self.w.call("POST", "/seats", self.w.acme, {"seats": 0}).status, 400)


class InvoiceRunTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_invoice_has_seats_and_tax(self):
        self.w.run_invoices()
        inv = self.w.invoices(self.w.acme)
        self.assertEqual(len(inv), 1)
        self.assertEqual((inv[0]["period"], inv[0]["subtotal_cents"], inv[0]["tax_cents"], inv[0]["total_cents"]),
                         ("2026-06", 49_990, 3_999, 53_989))
        self.assertEqual(self.w.invoices(self.w.birch)[0]["tax_cents"], 2_999)

    def test_usage_over_the_allowance_is_billed_per_started_thousand(self):
        self.w.usage("u1", "cus_acme", 120_000, "2026-06-10T12:00:00")
        self.w.usage("u2", "cus_acme", 30_500, "2026-06-20T12:00:00")
        self.w.run_invoices()
        detail = self.w.call("GET", f"/invoices/{self.w.invoices(self.w.acme)[0]['id']}", self.w.acme).body
        self.assertEqual(detail["lines"][1], {"description": "API calls over allowance: 50,500", "amount_cents": 2_550})

    def test_usage_events_are_deduplicated(self):
        self.w.usage("u1", "cus_acme", 150_000, "2026-06-10T12:00:00")
        self.w.usage("u1", "cus_acme", 150_000, "2026-06-10T12:00:00")
        self.w.run_invoices()
        self.assertEqual(self.w.invoices(self.w.acme)[0]["subtotal_cents"], 49_990 + 2_500)

    def test_seat_charges_are_invoiced_once(self):
        self.w.clock._now = datetime(2026, 6, 1, 9, 0)
        self.w.call("POST", "/seats", self.w.acme, {"seats": 11})
        self.w.clock._now = datetime(2026, 7, 1, 2, 0)
        self.w.run_invoices("2026-06")
        self.w.clock._now = datetime(2026, 8, 1, 2, 0)
        self.w.run_invoices("2026-07")
        june, july = sorted(self.w.invoices(self.w.acme), key=lambda i: i["period"])
        self.assertEqual(june["subtotal_cents"], 54_989 + 4_999)
        self.assertEqual(july["subtotal_cents"], 54_989)

    def test_invoices_are_private(self):
        self.w.run_invoices()
        acme_invoice = self.w.invoices(self.w.acme)[0]["id"]
        self.assertEqual(self.w.call("GET", f"/invoices/{acme_invoice}", self.w.birch).status, 404)


class PaymentsTest(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.run_invoices()
        self.invoice = self.w.invoices(self.w.acme)[0]

    def tearDown(self):
        self.w.cleanup()

    def test_payment_marks_the_invoice_paid(self):
        self.assertEqual(self.w.paid(self.invoice["id"], "pay_1", 53_989).status, 200)
        self.assertEqual(self.w.invoices(self.w.acme)[0]["status"], "paid")

    def test_partial_payment_leaves_it_open(self):
        self.w.paid(self.invoice["id"], "pay_1", 20_000)
        self.assertEqual(self.w.invoices(self.w.acme)[0]["status"], "open")

    def test_wrong_secret(self):
        resp = self.w.call("POST", "/webhooks/paygate", headers={"X-Paygate-Secret": "nope"}, body={"type": "payment.succeeded"})
        self.assertEqual(resp.status, 401)


if __name__ == "__main__":
    unittest.main()
