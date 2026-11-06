import unittest

from tests.helpers import PASSWORD, World


class LoginTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_login_and_me(self):
        resp = self.w.login("ada@acme.example")
        self.assertEqual(resp.status, 200)
        me = self.w.call("GET", "/me", resp.body["session_token"]).body
        self.assertEqual(me["email"], "ada@acme.example")
        self.assertIn("users:write", me["permissions"])

    def test_email_is_case_insensitive(self):
        self.assertEqual(self.w.login("Ada@Acme.Example").status, 200)

    def test_wrong_password(self):
        self.assertEqual(self.w.login("ada@acme.example", "nope").status, 401)

    def test_account_locks_after_five_failures(self):
        for _ in range(5):
            self.w.login("ben@acme.example", "guess")
        self.assertEqual(self.w.login("ben@acme.example").status, 429)
        self.w.clock.advance(minutes=16)
        self.assertEqual(self.w.login("ben@acme.example").status, 200)

    def test_idle_session_expires(self):
        token = self.w.token("ben@acme.example")
        self.w.clock.advance(minutes=31)
        self.assertEqual(self.w.call("GET", "/me", token).status, 401)

    def test_activity_keeps_the_session_alive(self):
        token = self.w.token("ben@acme.example")
        for _ in range(4):
            self.w.clock.advance(minutes=20)
            self.assertEqual(self.w.call("GET", "/me", token).status, 200)

    def test_logout(self):
        token = self.w.token("ben@acme.example")
        self.assertEqual(self.w.call("POST", "/logout", token).status, 204)
        self.assertEqual(self.w.call("GET", "/me", token).status, 401)


class ResetTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_reset_flow(self):
        old_session = self.w.token("ben@acme.example")
        self.assertEqual(self.w.call("POST", "/password-reset", body={"email": "ben@acme.example"}).status, 202)
        token = self.w.reset_link_token()
        resp = self.w.call("POST", "/password-reset/confirm", body={"token": token, "password": "New-Password-2026"})
        self.assertEqual(resp.status, 204)
        self.assertEqual(self.w.login("ben@acme.example", "New-Password-2026").status, 200)
        self.assertEqual(self.w.login("ben@acme.example", PASSWORD).status, 401)
        self.assertEqual(self.w.call("GET", "/me", old_session).status, 401)

    def test_unknown_email_still_202_and_sends_nothing(self):
        self.assertEqual(self.w.call("POST", "/password-reset", body={"email": "nobody@acme.example"}).status, 202)
        self.assertEqual(self.w.email.calls, [])

    def test_expired_link(self):
        self.w.call("POST", "/password-reset", body={"email": "ben@acme.example"})
        token = self.w.reset_link_token()
        self.w.clock.advance(minutes=31)
        resp = self.w.call("POST", "/password-reset/confirm", body={"token": token, "password": "New-Password-2026"})
        self.assertEqual(resp.status, 401)

    def test_weak_password(self):
        self.w.call("POST", "/password-reset", body={"email": "ben@acme.example"})
        resp = self.w.call("POST", "/password-reset/confirm", body={"token": self.w.reset_link_token(), "password": "short"})
        self.assertEqual(resp.status, 400)


class AdminTest(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.ada = self.w.token("ada@acme.example")

    def tearDown(self):
        self.w.cleanup()

    def test_admin_creates_users_in_own_org(self):
        resp = self.w.call("POST", "/admin/users", self.ada, {"email": "dan@acme.example", "password": "Dans-Password-1"})
        self.assertEqual(resp.status, 201)
        emails = [u["email"] for u in self.w.call("GET", "/admin/users", self.ada).body["users"]]
        self.assertEqual(emails, ["ada@acme.example", "ben@acme.example", "dan@acme.example"])

    def test_members_cannot_administer(self):
        ben = self.w.token("ben@acme.example")
        self.assertEqual(self.w.call("GET", "/admin/users", ben).status, 403)

    def test_granting_support_lets_a_user_read_users(self):
        self.assertEqual(self.w.call("POST", "/admin/users/usr_ben/roles", self.ada, {"role": "support"}).status, 200)
        ben = self.w.token("ben@acme.example")
        self.assertEqual(self.w.call("GET", "/admin/users", ben).status, 200)

    def test_other_orgs_users_are_invisible(self):
        self.assertEqual(self.w.call("POST", "/admin/users/usr_cara/roles", self.ada, {"role": "member"}).status, 404)


if __name__ == "__main__":
    unittest.main()
