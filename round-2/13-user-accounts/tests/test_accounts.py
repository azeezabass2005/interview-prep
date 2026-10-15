import unittest

from tests.helpers import PW, World


class TestAccounts(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_signup_and_login(self):
        self.assertEqual(self.w.signup().status, 201)
        self.assertEqual(self.w.login().status, 200)

    def test_same_email_twice(self):
        self.w.signup()
        self.assertEqual(self.w.signup().status, 409)

    def test_wrong_password(self):
        self.w.signup()
        self.assertEqual(self.w.login(password="nope nope nope").status, 401)

    def test_validation(self):
        self.assertEqual(self.w.signup(email="not-an-email").status, 400)
        self.assertEqual(self.w.signup(password="short").status, 400)

    def test_password_reset(self):
        self.w.signup()
        token = self.w.api.reset.request_reset("ann@example.com")
        self.assertEqual(self.w.api.post_reset({"token": token, "password": "brand new password"}).status, 200)
        self.assertEqual(self.w.login(password="brand new password").status, 200)

    def test_expired_reset_token(self):
        self.w.signup()
        token = self.w.api.reset.request_reset("ann@example.com")
        self.w.clock.advance(minutes=61)
        self.assertEqual(self.w.api.post_reset({"token": token, "password": "brand new password"}).status, 400)

    def test_directory_search(self):
        self.w.signup()
        self.w.signup(email="bob@example.com", name="Bob Annis")
        self.assertEqual([r["display_name"] for r in self.w.api.get_directory("An").body["results"]], ["Ann Lee"])

    def test_successful_login_resets_failures(self):
        self.w.signup()
        for _ in range(3):
            self.w.login(password="wrong wrong wrong")
        self.w.login()
        self.assertEqual(self.w.users.by_email("ann@example.com").failed_attempts, 0)


if __name__ == "__main__":
    unittest.main()
