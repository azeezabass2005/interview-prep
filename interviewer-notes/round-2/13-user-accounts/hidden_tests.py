import threading
import unittest
from unittest import mock

from accounts.errors import InvalidToken
from accounts.repositories.tokens import TokenRepository
from accounts.services.reset import PasswordResetService
from tests.helpers import World


class HiddenAccounts(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_ACC1301_email_case_and_spaces(self):
        self.w.signup()
        self.assertEqual(self.w.signup(email=" Ann@Example.com ").status, 409)
        self.assertEqual(self.w.login(email="ANN@EXAMPLE.COM").status, 200)

    def test_ACC1302_reset_token_single_use(self):
        self.w.signup()
        token = self.w.api.reset.request_reset("ann@example.com")
        a, b = PasswordResetService(self.w.db, self.w.clock), PasswordResetService(self.w.db, self.w.clock)
        barrier = threading.Barrier(2, timeout=3)
        original = TokenRepository.get
        calls = {"n": 0}
        lock = threading.Lock()

        def paused(repo, t):
            result = original(repo, t)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        outcomes = []

        def run(svc, pw):
            try:
                svc.reset(token, pw)
                outcomes.append("ok")
            except InvalidToken:
                outcomes.append("rejected")

        with mock.patch.object(TokenRepository, "get", paused):
            threads = [threading.Thread(target=run, args=(a, "attacker password 1")),
                       threading.Thread(target=run, args=(b, "attacker password 2"))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(sorted(outcomes), ["ok", "rejected"])
        self.assertEqual(self.w.api.post_reset({"token": token, "password": "third password!!"}).status, 400)

    def test_ACC1303_locked_account_rejects_correct_password(self):
        self.w.signup()
        for _ in range(5):
            self.w.login(password="wrong wrong wrong")
        self.assertEqual(self.w.login().status, 423)
        self.w.clock.advance(minutes=16)
        self.assertEqual(self.w.login().status, 200)

    def test_ACC1304_deleted_users_hidden_from_directory(self):
        user_id = self.w.signup().body["user_id"]
        self.w.users.soft_delete(user_id, self.w.clock.now())
        self.assertEqual(self.w.api.get_directory("An").body["results"], [])
