import unittest
from datetime import timedelta

from portal.clock import iso
from tests.helpers import NOW, World


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_res101_open_ended_subscription_does_not_leak_to_other_firms(self):
        hartwell = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        norland = self.w.client_user("org_norland", "usr_nora", sectors=["tech"], ends_on=None)
        tech = self.w.published("Chip cycle", "tech")
        self.assertEqual(self.w.call("GET", f"/reports/{tech.id}", hartwell).status, 403)
        self.w.c.cache.clear()
        self.assertEqual(self.w.call("GET", "/reports", hartwell).body["items"], [])
        self.assertEqual(self.w.call("GET", f"/reports/{tech.id}", norland).status, 200)

    def test_res104_list_cache_is_per_firm(self):
        energy = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        rates = self.w.client_user("org_brook", "usr_bea", sectors=["rates"])
        self.w.published("Oil outlook", "energy")
        self.w.published("Curve steepener", "rates")
        self.assertEqual([r["title"] for r in self.w.call("GET", "/reports", energy).body["items"]], ["Oil outlook"])
        self.assertEqual([r["title"] for r in self.w.call("GET", "/reports", rates).body["items"]], ["Curve steepener"])
        before = len(self.w.db.statements)
        self.w.call("GET", "/reports", rates)
        self.assertEqual([s for s in self.w.db.statements[before:] if "FROM reports" in s], [], "list should still be cached")

    def test_res110_pages_do_not_overlap(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        for i in range(25):
            self.w.published(f"Note {i:02d}", "energy", NOW - timedelta(hours=i))
        p1 = self.w.call("GET", "/reports?page=1&page_size=20", token).body
        p2 = self.w.call("GET", "/reports?page=2&page_size=20", token).body
        self.assertEqual(len(p1["items"]), 20)
        self.assertTrue(p1["has_more"])
        self.assertEqual(len(p2["items"]), 5)
        self.assertFalse(p2["has_more"])
        self.assertEqual({r["id"] for r in p1["items"]} & {r["id"] for r in p2["items"]}, set())

    def test_res115_query_string_tokens_are_not_logged(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        report = self.w.published("Oil outlook", "energy")
        resp = self.w.call("GET", f"/reports/{report.id}/pdf?access_token={token}&utm=email")
        self.assertEqual(resp.status, 200)
        logged = str(self.w.c.logger.records)
        self.assertNotIn(token, logged)
        self.assertIn("utm", logged)

    def test_res120_failed_digest_is_retried_and_not_skipped(self):
        self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        self.w.published("Oil outlook", "energy", NOW - timedelta(hours=1))
        from portal.adapters.transport import HttpResult
        self.w.email.queue(HttpResult(503, {"error": "unavailable"}))
        self.w.c.digest.schedule_all()
        self.w.c.worker.run_pending()
        self.assertEqual(self.w.c.users.get("usr_hal").last_digest_at, None)
        self.assertEqual(len(self.w.c.queue.by_status("queued")), 1, "the failed send should be retried")
        self.w.clock.advance(minutes=5)
        self.w.c.worker.run_pending()
        self.assertEqual(len(self.w.email.calls), 2)
        self.assertIn("Oil outlook", self.w.email.calls[-1].json()["html"])
        self.assertIsNotNone(self.w.c.users.get("usr_hal").last_digest_at)


if __name__ == "__main__":
    unittest.main()
