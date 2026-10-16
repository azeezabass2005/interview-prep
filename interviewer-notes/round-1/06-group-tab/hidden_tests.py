import unittest

from tab.app import build_app


def group(members=("ann", "bob", "cy", "dan")):
    api, _ = build_app()
    api.create_group({"group_id": "g", "name": "Trip", "members": list(members)})
    return api


class HiddenTab(unittest.TestCase):
    def test_B1_equal_split_keeps_every_cent(self):
        api = group()
        _, body = api.add_expense("g", {"payer": "ann", "amount_cents": 1000, "split": "EQUAL", "details": ["ann", "bob", "cy"]})
        self.assertEqual(body["shares"], {"ann": 334, "bob": 333, "cy": 333})
        self.assertEqual(sum(api.balances("g")[1].values()), 0)

    def test_B2_weighted_leftover_by_largest_remainder(self):
        api = group()
        _, body = api.add_expense("g", {"payer": "ann", "amount_cents": 100, "split": "SHARES", "details": {"ann": 1, "bob": 2}})
        self.assertEqual(body["shares"], {"ann": 33, "bob": 67})

    def test_B3_deleted_expenses_ignored(self):
        api = group()
        _, body = api.add_expense("g", {"payer": "ann", "amount_cents": 900, "split": "EQUAL", "details": ["ann", "bob", "cy"]})
        api.delete_expense(body["expense_id"])
        self.assertTrue(all(v == 0 for v in api.balances("g")[1].values()))

    def test_B4_payment_settles_debt(self):
        api = group(("ann", "bob"))
        api.add_expense("g", {"payer": "ann", "amount_cents": 3000, "split": "EQUAL", "details": ["ann", "bob"]})
        api.pay("g", {"from": "bob", "to": "ann", "amount_cents": 1500})
        self.assertEqual(api.balances("g")[1], {"ann": 0, "bob": 0})

    def test_B5_settle_up_matches_largest(self):
        api = group()
        api.add_expense("g", {"payer": "ann", "amount_cents": 5000, "split": "EXACT", "details": {"cy": 5000}})
        api.add_expense("g", {"payer": "bob", "amount_cents": 3000, "split": "EXACT", "details": {"dan": 3000}})
        self.assertEqual(api.settle_up("g")[1]["transfers"],
                         [{"from": "cy", "to": "ann", "amount_cents": 5000}, {"from": "dan", "to": "bob", "amount_cents": 3000}])
