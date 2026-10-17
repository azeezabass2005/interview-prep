import unittest
from datetime import datetime

from accounts import Accounts

PASSWORD = "correct-horse-42"


class Clock:
    def __init__(self):
        self.current = datetime(2026, 5, 4, 9, 0)

    def now(self):
        return self.current


def accounts():
    a = Accounts(Clock())
    a.sign_up("ana@example.com", PASSWORD)
    return a


class HiddenAccounts(unittest.TestCase):
    def test_B1_email_unique_ignoring_case(self):
        with self.assertRaises(Exception):
            accounts().sign_up("ANA@example.com", "another-pass-77")

    def test_B2_password_must_not_contain_local_part(self):
        with self.assertRaises(Exception):
            Accounts(Clock()).sign_up("bob@example.com", "xxBOB12345678")

    def test_B3_failures_must_be_consecutive(self):
        a = accounts()
        for _ in range(4):
            a.login("ana@example.com", "wrong")
        a.login("ana@example.com", PASSWORD)
        for _ in range(4):
            a.login("ana@example.com", "wrong")
        self.assertTrue(a.login("ana@example.com", PASSWORD))

    def test_B4_token_single_use(self):
        a = accounts()
        token = a.request_reset("ana@example.com")
        a.reset("ana@example.com", token, "new-password-99")
        with self.assertRaises(Exception):
            a.reset("ana@example.com", token, "other-password-11")

    def test_B5_reset_unlocks(self):
        a = accounts()
        for _ in range(5):
            a.login("ana@example.com", "wrong")
        token = a.request_reset("ana@example.com")
        a.reset("ana@example.com", token, "new-password-99")
        self.assertTrue(a.login("ana@example.com", "new-password-99"))
