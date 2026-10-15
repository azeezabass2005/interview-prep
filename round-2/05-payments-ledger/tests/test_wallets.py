import unittest

from ledger.services.money import format_cents, parse_amount
from tests.helpers import World


class TestMoney(unittest.TestCase):
    def test_parse_whole_and_cents(self):
        self.assertEqual(parse_amount("12"), 1200)
        self.assertEqual(parse_amount("0.25"), 25)

    def test_format(self):
        self.assertEqual(format_cents(1005), "10.05")
        self.assertEqual(format_cents(-50), "-0.50")


class TestWallets(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.wallets.open_account("A", "ann")
        self.w.wallets.open_account("B", "bob")

    def tearDown(self):
        self.w.cleanup()

    def test_deposit_and_withdraw(self):
        self.w.api.post_deposit("A", {"amount": "100.00"})
        resp = self.w.api.post_withdrawal("A", {"amount": "30.00"})
        self.assertEqual(resp.body["balance"], "70.00")

    def test_insufficient_funds(self):
        self.w.api.post_deposit("A", {"amount": "10.00"})
        self.assertEqual(self.w.api.post_withdrawal("A", {"amount": "10.01"}).status, 409)

    def test_transfer(self):
        self.w.api.post_deposit("A", {"amount": "100.00"})
        self.assertEqual(self.w.api.post_transfer({"from": "A", "to": "B", "amount": "40.00"}).status, 200)
        self.assertEqual(self.w.api.get_account("B").body["balance"], "40.00")
        self.assertEqual(self.w.entries.sum_for("A"), 6000)

    def test_closed_account_cannot_deposit(self):
        self.w.wallets.close_account("B")
        self.assertEqual(self.w.api.post_deposit("B", {"amount": "1.00"}).status, 409)

    def test_bad_amount(self):
        self.assertEqual(self.w.api.post_deposit("A", {"amount": "abc"}).status, 400)
        self.assertEqual(self.w.api.post_deposit("A", {"amount": "-5"}).status, 400)


class TestStatements(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.wallets.open_account("A", "ann")

    def tearDown(self):
        self.w.cleanup()

    def test_paging_distinct_timestamps(self):
        for i in range(5):
            self.w.api.post_deposit("A", {"amount": "1.00", "reference": f"d{i}"})
            self.w.clock.advance(1)
        first = self.w.api.get_statement("A", limit=2).body
        second = self.w.api.get_statement("A", cursor=first["next_cursor"], limit=2).body
        self.assertEqual([e["reference"] for e in first["entries"] + second["entries"]], ["d0", "d1", "d2", "d3"])


if __name__ == "__main__":
    unittest.main()
