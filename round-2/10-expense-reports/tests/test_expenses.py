import unittest

from tests.helpers import World


class EmployeeFlowTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_create_add_and_total(self):
        rid = self.w.report(self.w.eli)
        self.assertEqual(self.w.expense(self.w.eli, rid, 4_250).status, 201)
        self.w.expense(self.w.eli, rid, 1_000, category="travel")
        body = self.w.call("GET", f"/reports/{rid}", self.w.eli).body
        self.assertEqual((len(body["expenses"]), body["total_usd_cents"]), (2, 5_250))

    def test_foreign_currency_uses_the_rate_on_the_expense_date(self):
        rid = self.w.report(self.w.eli)
        resp = self.w.expense(self.w.eli, rid, 10_000, currency="EUR", spent_on="2026-06-02")
        self.assertEqual(resp.body["usd_cents"], 10_800)
        self.assertEqual(self.w.fx.calls[-1]["date"], "2026-06-02")

    def test_zero_decimal_currency(self):
        rid = self.w.report(self.w.eli)
        self.assertEqual(self.w.expense(self.w.eli, rid, 5_000, currency="JPY").body["usd_cents"], 3_200)

    def test_validation(self):
        rid = self.w.report(self.w.eli)
        self.assertEqual(self.w.expense(self.w.eli, rid, 0).status, 400)
        self.assertEqual(self.w.expense(self.w.eli, rid, currency="XYZ").status, 400)
        self.assertEqual(self.w.expense(self.w.eli, rid, spent_on="2026-07-01").status, 400)
        self.assertEqual(self.w.expense(self.w.eli, rid, category="yacht").status, 400)

    def test_edit_merchant_and_amount(self):
        rid = self.w.report(self.w.eli)
        exp = self.w.expense(self.w.eli, rid).body
        resp = self.w.call("PATCH", f"/expenses/{exp['id']}", self.w.eli, {"merchant": "Bistro", "amount_minor": 5_000})
        self.assertEqual((resp.body["merchant"], resp.body["usd_cents"]), ("Bistro", 5_000))

    def test_delete_removes_from_the_list(self):
        rid = self.w.report(self.w.eli)
        exp = self.w.expense(self.w.eli, rid).body
        self.assertEqual(self.w.call("DELETE", f"/expenses/{exp['id']}", self.w.eli).status, 204)
        self.assertEqual(self.w.call("GET", f"/reports/{rid}", self.w.eli).body["expenses"], [])

    def test_submitted_reports_are_locked(self):
        rid = self.w.submitted_report(self.w.eli)
        self.assertEqual(self.w.expense(self.w.eli, rid).status, 409)

    def test_cannot_submit_empty(self):
        self.assertEqual(self.w.call("POST", f"/reports/{self.w.report(self.w.eli)}/submit", self.w.eli).status, 400)

    def test_others_cannot_see_my_report(self):
        rid = self.w.report(self.w.eli)
        self.assertEqual(self.w.call("GET", f"/reports/{rid}", self.w.finn).status, 404)
        self.assertEqual(self.w.call("GET", f"/reports/{rid}", self.w.zoe).status, 404)


class ApprovalTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_manager_approves_a_direct_report(self):
        rid = self.w.submitted_report(self.w.eli)
        self.assertEqual([r["id"] for r in self.w.call("GET", "/team/reports", self.w.maria).body["reports"]], [rid])
        resp = self.w.call("POST", f"/reports/{rid}/approve", self.w.maria)
        self.assertEqual((resp.status, resp.body["status"], resp.body["decided_by"]), (200, "approved", "emp_maria"))

    def test_employees_cannot_approve(self):
        rid = self.w.submitted_report(self.w.eli)
        self.assertEqual(self.w.call("POST", f"/reports/{rid}/approve", self.w.finn).status, 403)

    def test_no_self_approval(self):
        rid = self.w.submitted_report(self.w.maria)
        self.assertEqual(self.w.call("POST", f"/reports/{rid}/approve", self.w.maria).status, 403)

    def test_managers_can_view_reports_in_their_organisation(self):
        rid = self.w.submitted_report(self.w.finn)
        self.assertEqual(self.w.call("GET", f"/reports/{rid}", self.w.maria).status, 200)
        self.assertEqual(self.w.call("GET", f"/reports/{rid}", self.w.zoe).status, 404)


class ReceiptsTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_receipt_total_is_read(self):
        rid = self.w.report(self.w.eli)
        exp = self.w.expense(self.w.eli, rid).body
        self.assertEqual(self.w.call("POST", f"/expenses/{exp['id']}/receipt", self.w.eli, {"image": "jpg..total=42.50"}).status, 202)
        self.w.c.scanner.schedule()
        self.w.c.worker.run_pending()
        expense = self.w.call("GET", f"/reports/{rid}", self.w.eli).body["expenses"][0]
        self.assertEqual((expense["receipt_status"], expense["receipt_total"]), ("done", "42.50"))


if __name__ == "__main__":
    unittest.main()
