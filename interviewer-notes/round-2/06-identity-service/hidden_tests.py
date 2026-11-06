import unittest

from tests.helpers import PASSWORD, World


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_iam601_reset_link_works_once(self):
        self.w.call("POST", "/password-reset", body={"email": "ben@acme.example"})
        token = self.w.reset_link_token()
        first = self.w.call("POST", "/password-reset/confirm", body={"token": token, "password": "First-Reset-2026"})
        second = self.w.call("POST", "/password-reset/confirm", body={"token": token, "password": "Second-Reset-2026"})
        self.assertEqual((first.status, second.status), (204, 401))
        self.assertEqual(self.w.login("ben@acme.example", "First-Reset-2026").status, 200)
        self.assertEqual(self.w.login("ben@acme.example", "Second-Reset-2026").status, 401)

    def test_iam605_sessions_end_after_twelve_hours(self):
        token = self.w.token("ben@acme.example")
        for _ in range(35):  # 11h40 of activity, every 20 minutes
            self.w.clock.advance(minutes=20)
            self.assertEqual(self.w.call("GET", "/me", token).status, 200)
        self.w.clock.advance(minutes=20)  # 12h00
        self.assertEqual(self.w.call("GET", "/me", token).status, 401)

    def test_iam610_lockout_ignores_email_case(self):
        for email in ("Ben@acme.example", "BEN@acme.example", "ben@ACME.example", "bEn@acme.example", "BeN@Acme.Example"):
            self.assertEqual(self.w.login(email, "guess").status, 401)
        self.assertEqual(self.w.login("ben@acme.example", PASSWORD).status, 429)

    def test_iam615_unknown_email_looks_like_wrong_password(self):
        unknown = self.w.login("nobody@acme.example", "whatever")
        wrong = self.w.login("ben@acme.example", "whatever")
        self.assertEqual(unknown.status, 401)
        strip = lambda b: {k: v for k, v in b["error"].items() if k != "request_id"}
        self.assertEqual(strip(unknown.body), strip(wrong.body))

    def test_iam620_revoked_role_applies_on_next_request(self):
        ada = self.w.token("ada@acme.example")
        self.w.call("POST", "/admin/users/usr_ben/roles", ada, {"role": "admin"})
        ben = self.w.token("ben@acme.example")
        self.assertEqual(self.w.call("GET", "/admin/users", ben).status, 200)
        self.assertEqual(self.w.call("DELETE", "/admin/users/usr_ben/roles/admin", ada).status, 200)
        self.assertEqual(self.w.call("GET", "/admin/users", ben).status, 403)


if __name__ == "__main__":
    unittest.main()
