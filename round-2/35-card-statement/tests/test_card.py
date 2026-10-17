import unittest

from card.app import build_app


class TestCard(unittest.TestCase):
    def test_first_statement(self):
        api = build_app()
        api.open("C1", "5000", "2026-03-01")
        api.post("C1", {"date": "2026-03-01", "kind": "PURCHASE", "amount": "1000"})
        status, statement = api.close("C1", "2026-03-30")
        self.assertEqual(status, 200)
        self.assertEqual(statement["interest"]["purchase"], "19.73")


if __name__ == "__main__":
    unittest.main()
