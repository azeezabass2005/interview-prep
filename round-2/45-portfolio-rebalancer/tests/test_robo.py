import unittest

from robo.app import build_app


class TestRobo(unittest.TestCase):
    def test_balanced_account_needs_nothing(self):
        api = build_app()
        api.model("M", {"AAA": 50, "BBB": 50})
        api.price("AAA", "50")
        api.price("BBB", "50")
        api.open({"account_id": "A", "model": "M", "cash": "200", "holdings": {"AAA": 98, "BBB": 98}})
        self.assertEqual(api.plan("A"), (200, {"trades": []}))


if __name__ == "__main__":
    unittest.main()
