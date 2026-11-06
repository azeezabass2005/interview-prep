import unittest

from tests.helpers import World


class PlatformTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_request_id_is_returned_and_logged(self):
        resp = self.w.call("GET", "/health", headers={"X-Request-ID": "req_abc"})
        self.assertEqual(resp.headers["X-Request-ID"], "req_abc")
        self.assertEqual(self.w.c.logger.events("request")[-1]["request_id"], "req_abc")

    def test_authorization_header_is_redacted_in_logs(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        self.w.call("GET", "/reports", token)
        logged = self.w.c.logger.events("request")[-1]
        self.assertEqual(logged["headers"]["Authorization"], "[REDACTED]")
        self.assertNotIn(token, str(self.w.c.logger.records))

    def test_errors_have_a_stable_shape(self):
        resp = self.w.call("GET", "/nope", self.w.analyst)
        self.assertEqual(resp.status, 404)
        self.assertEqual(resp.body["error"]["code"], "not_found")

    def test_list_is_cached(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        self.w.call("GET", "/reports", token)
        before = len(self.w.db.statements)
        self.w.call("GET", "/reports", token)
        reports_queries = [s for s in self.w.db.statements[before:] if "FROM reports" in s]
        self.assertEqual(reports_queries, [])

    def test_rate_limit(self):
        token = self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        statuses = [self.w.call("GET", "/reports", token).status for _ in range(121)]
        self.assertEqual(statuses[-1], 429)
        self.assertEqual(statuses.count(200), 120)


if __name__ == "__main__":
    unittest.main()
