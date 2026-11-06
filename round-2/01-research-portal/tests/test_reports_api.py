import unittest
from datetime import timedelta

from tests.helpers import NOW, World


class ReportsApiTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_requires_a_token(self):
        self.assertEqual(self.w.call("GET", "/reports").status, 401)
        self.assertEqual(self.w.call("GET", "/health").status, 200)

    def test_client_lists_entitled_reports_newest_first(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        self.w.published("Oil outlook", "energy", NOW - timedelta(days=2))
        self.w.published("Gas storage", "energy", NOW - timedelta(days=1))
        self.w.published("Chip cycle", "tech", NOW - timedelta(days=1))
        resp = self.w.call("GET", "/reports", token)
        self.assertEqual(resp.status, 200)
        self.assertEqual([r["title"] for r in resp.body["items"]], ["Gas storage", "Oil outlook"])
        self.assertFalse(resp.body["has_more"])

    def test_read_a_report_in_an_entitled_sector(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        report = self.w.published("Oil outlook", "energy")
        resp = self.w.call("GET", f"/reports/{report.id}", token)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.body["body"], "Oil outlook body")

    def test_unentitled_sector_is_forbidden(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        report = self.w.published("Chip cycle", "tech")
        self.assertEqual(self.w.call("GET", f"/reports/{report.id}", token).status, 403)

    def test_expired_subscription_is_not_entitled(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"], starts_on="2025-01-01",
                                   ends_on="2026-01-01")
        report = self.w.published("Oil outlook", "energy")
        self.assertEqual(self.w.call("GET", f"/reports/{report.id}", token).status, 403)

    def test_analyst_drafts_and_publishes(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["rates"])
        draft = self.w.call("POST", "/reports", self.w.analyst,
                            {"title": "Curve steepener", "sector": "rates", "summary": "2s10s", "body": "..."})
        self.assertEqual(draft.status, 201)
        self.assertEqual(self.w.call("GET", "/reports", token).body["items"], [])
        self.assertEqual(self.w.call("POST", f"/reports/{draft.body['id']}/publish", self.w.analyst).status, 200)
        self.assertEqual([r["title"] for r in self.w.call("GET", "/reports", token).body["items"]], ["Curve steepener"])

    def test_clients_cannot_publish(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["rates"])
        resp = self.w.call("POST", "/reports", token, {"title": "x", "sector": "rates", "summary": "y", "body": ""})
        self.assertEqual(resp.status, 403)

    def test_validation_errors(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["rates"])
        self.assertEqual(self.w.call("GET", "/reports?page=0", token).status, 400)
        self.assertEqual(self.w.call("GET", "/reports?sector=crypto", token).status, 400)
        self.assertEqual(self.w.call("GET", "/reports?page_size=abc", token).status, 400)

    def test_read_stats_are_internal_only(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        report = self.w.published("Oil outlook", "energy")
        self.w.call("GET", f"/reports/{report.id}", token)
        self.w.call("GET", f"/reports/{report.id}", token)
        self.assertEqual(self.w.call("GET", f"/reports/{report.id}/stats", token).status, 403)
        self.assertEqual(self.w.call("GET", f"/reports/{report.id}/stats", self.w.analyst).body, {"reads": 2, "readers": 1})


if __name__ == "__main__":
    unittest.main()
