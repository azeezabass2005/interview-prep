import unittest
from datetime import datetime

from billing.adapters.transport import TransportTimeout
from tests.helpers import World


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_bil701_rerunning_the_invoice_run_does_not_duplicate(self):
        self.w.run_invoices("2026-06")
        self.w.run_invoices("2026-06")
        self.assertEqual([i["period"] for i in self.w.invoices(self.w.acme)], ["2026-06"])
        self.assertEqual([i["period"] for i in self.w.invoices(self.w.birch)], ["2026-06"])

    def test_bil705_midnight_usage_belongs_to_the_new_month(self):
        self.w.usage("u1", "cus_acme", 100_000, "2026-06-15T12:00:00")
        self.w.usage("u2", "cus_acme", 1_000, "2026-07-01T00:00:00")
        self.w.run_invoices("2026-06")
        self.assertEqual(self.w.invoices(self.w.acme)[0]["subtotal_cents"], 49_990)

    def test_bil710_proration_rounds_half_up_in_integer_cents(self):
        self.assertEqual(self.w.call("POST", "/seats", self.w.birch, {"seats": 6}).body["prorated_charge_cents"], 7_499)
        self.w.clock._now = datetime(2026, 6, 30, 9, 0)
        self.assertEqual(self.w.call("POST", "/seats", self.w.acme, {"seats": 13}).body["prorated_charge_cents"], 500)

    def test_bil715_one_tax_failure_does_not_stop_the_run(self):
        self.w.c.customers.add("cus_cedar", "Cedar Funds", "US", 2, 4_999)
        original = self.w.tax.send
        calls = {"n": 0}

        def flaky(*args):
            calls["n"] += 1
            if calls["n"] == 2:
                raise TransportTimeout("taxly timed out")
            return original(*args)

        self.w.tax.send = flaky
        self.w.run_invoices("2026-06")
        statuses = {cid: self.w.c.invoices.for_customer(cid) for cid in ("cus_acme", "cus_birch", "cus_cedar")}
        self.assertEqual({cid: [r["status"] for r in rows] for cid, rows in statuses.items()},
                         {"cus_acme": ["open"], "cus_birch": ["pending_tax"], "cus_cedar": ["open"]})
        self.assertEqual(statuses["cus_birch"][0]["tax_cents"], 0)
        self.assertEqual(statuses["cus_cedar"][0]["tax_cents"], 799)

    def test_bil720_redelivered_payment_is_recorded_once(self):
        self.w.run_invoices()
        invoice = self.w.invoices(self.w.acme)[0]
        self.assertEqual(self.w.paid(invoice["id"], "pay_1", 20_000).status, 200)
        self.assertEqual(self.w.paid(invoice["id"], "pay_1", 20_000).status, 200)
        self.w.paid(invoice["id"], "pay_2", 33_989, event_id="evt_2")
        detail = self.w.call("GET", f"/invoices/{invoice['id']}", self.w.acme).body
        self.assertEqual([p["amount_cents"] for p in detail["payments"]], [20_000, 33_989])
        self.assertEqual(detail["status"], "paid")


if __name__ == "__main__":
    unittest.main()
