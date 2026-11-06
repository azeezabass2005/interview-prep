import unittest

from tests.helpers import World


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_exp1001_only_the_employees_manager_can_decide(self):
        rid = self.w.submitted_report(self.w.finn)
        self.assertEqual(self.w.call("POST", f"/reports/{rid}/approve", self.w.maria).status, 403)
        self.assertEqual(self.w.call("GET", f"/reports/{rid}", self.w.maria).body["status"], "submitted")
        self.assertEqual(self.w.call("POST", f"/reports/{rid}/approve", self.w.omar).status, 200)

    def test_exp1005_each_expense_uses_its_own_dates_rate(self):
        rid = self.w.report(self.w.eli)
        first = self.w.expense(self.w.eli, rid, 10_000, currency="EUR", spent_on="2026-06-02").body
        second = self.w.expense(self.w.eli, rid, 10_000, currency="EUR", spent_on="2026-06-18").body
        self.assertEqual((first["usd_cents"], second["usd_cents"]), (10_800, 11_500))
        calls = len(self.w.fx.calls)
        self.w.expense(self.w.eli, rid, 5_000, currency="EUR", spent_on="2026-06-02")
        self.assertEqual(len(self.w.fx.calls), calls)

    def test_exp1010_one_bad_receipt_does_not_block_the_batch(self):
        rid = self.w.report(self.w.eli)
        ids = [self.w.expense(self.w.eli, rid, merchant=f"M{i}").body["id"] for i in range(3)]
        for exp_id, image in zip(ids, ["jpg..total=10.00", "jpg..blurry", "jpg..total=30.00"]):
            self.w.call("POST", f"/expenses/{exp_id}/receipt", self.w.eli, {"image": image})
        self.w.c.scanner.schedule()
        self.w.c.worker.run_pending()
        lines = {e["id"]: e for e in self.w.call("GET", f"/reports/{rid}", self.w.eli).body["expenses"]}
        self.assertEqual([lines[i]["receipt_status"] for i in ids], ["done", "failed", "done"])
        self.assertIn("unreadable", lines[ids[1]]["receipt_error"])

    def test_exp1015_deleted_lines_do_not_count(self):
        rid = self.w.report(self.w.eli)
        big = self.w.expense(self.w.eli, rid, 3_000_000, category="travel").body
        self.w.expense(self.w.eli, rid, 30_000)
        self.w.call("DELETE", f"/expenses/{big['id']}", self.w.eli)
        self.assertEqual(self.w.call("GET", f"/reports/{rid}", self.w.eli).body["total_usd_cents"], 30_000)
        self.assertEqual(self.w.call("POST", f"/reports/{rid}/submit", self.w.eli).status, 200)

    def test_exp1020_only_documented_fields_are_editable(self):
        rid = self.w.report(self.w.eli)
        exp = self.w.expense(self.w.eli, rid, 4_000, currency="EUR").body
        resp = self.w.call("PATCH", f"/expenses/{exp['id']}", self.w.eli, {"usd_cents": 400_000})
        self.assertEqual(resp.status, 400)
        self.assertEqual(self.w.call("GET", f"/reports/{rid}", self.w.eli).body["total_usd_cents"], exp["usd_cents"])
        resp = self.w.call("PATCH", f"/expenses/{exp['id']}", self.w.eli, {"merchant": "Bistro", "receipt_status": "done"})
        self.assertEqual(resp.status, 400)
        self.assertEqual(self.w.call("PATCH", f"/expenses/{exp['id']}", self.w.eli, {"merchant": "Bistro"}).status, 200)


if __name__ == "__main__":
    unittest.main()
