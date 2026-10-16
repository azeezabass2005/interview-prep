import unittest

from tab.app import build_app


class TestTab(unittest.TestCase):
    def test_even_dinner(self):
        api, _ = build_app()
        api.create_group({"group_id": "g1", "name": "Trip", "members": ["ann", "bob"]})
        api.add_expense("g1", {"payer": "ann", "amount_cents": 3000, "split": "EQUAL", "details": ["ann", "bob"]})
        self.assertEqual(api.balances("g1"), (200, {"ann": 1500, "bob": -1500}))


if __name__ == "__main__":
    unittest.main()
