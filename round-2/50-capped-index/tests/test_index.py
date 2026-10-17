import unittest

from indexing.app import build_app


class TestIndex(unittest.TestCase):
    def test_two_equal_constituents(self):
        api = build_app()
        api.define("IDX", "0.6")
        api.security("A", 100_000_000, "1.0", "10", "2020-01-01")
        api.security("B", 100_000_000, "1.0", "10", "2020-01-01")
        status, body = api.rebalance("IDX", "2026-06-19")
        self.assertEqual(status, 200)
        self.assertEqual(body["weights"], {"A": "50.0000", "B": "50.0000"})


if __name__ == "__main__":
    unittest.main()
