import unittest

from tests.helpers import World


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_small_expense_one_approval_and_payment(self):
        eid = self.w.submit()
        self.assertEqual(self.w.api.post_approve(eid, "mark").body["status"], "APPROVED")
        self.assertEqual(self.w.payments.count_for(eid), 1)

    def test_large_usd_expense_needs_director(self):
        eid = self.w.submit(amount="7500")
        self.assertEqual(self.w.api.post_approve(eid, "mark").body["status"], "PENDING_DIRECTOR")
        self.assertEqual(self.w.api.post_approve(eid, "mia").status, 403)
        self.assertEqual(self.w.api.post_approve(eid, "dora").body["status"], "APPROVED")

    def test_employee_cannot_approve(self):
        eid = self.w.submit(who="mark")
        self.assertEqual(self.w.api.post_approve(eid, "emma").status, 403)

    def test_cannot_approve_twice_sequentially(self):
        eid = self.w.submit()
        self.w.api.post_approve(eid, "mark")
        self.assertEqual(self.w.api.post_approve(eid, "mark").status, 409)

    def test_validation(self):
        resp = self.w.api.post_expense("emma", {"amount": "-1", "currency": "USD", "date": "2026-03-01"})
        self.assertEqual(resp.status, 400)

    def test_usd_only_report(self):
        self.w.submit(amount="100.00")
        self.w.submit(amount="50.00")
        self.assertEqual(self.w.api.get_team_report("london", 2026, 3).body["total_usd"], "150.00")


if __name__ == "__main__":
    unittest.main()
