import unittest
from datetime import datetime

from accounts import Accounts


class Clock:
    def __init__(self):
        self.current = datetime(2026, 5, 4, 9, 0)

    def now(self):
        return self.current


class TestAccounts(unittest.TestCase):
    def test_sign_up_and_login(self):
        accounts = Accounts(Clock())
        accounts.sign_up("ana@example.com", "correct-horse-42")
        self.assertTrue(accounts.login("ana@example.com", "correct-horse-42"))


if __name__ == "__main__":
    unittest.main()
