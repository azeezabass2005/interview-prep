import unittest

from rebalance import Account, Rebalancer


class TestRebalance(unittest.TestCase):
    def test_balanced_account_needs_nothing(self):
        r = Rebalancer({"AAA": 100, "BBB": 100})
        account = Account(cash=0, shares={"AAA": 50, "BBB": 50})
        self.assertEqual(r.plan(account, {"AAA": "0.5", "BBB": "0.5"}), [])


if __name__ == "__main__":
    unittest.main()
