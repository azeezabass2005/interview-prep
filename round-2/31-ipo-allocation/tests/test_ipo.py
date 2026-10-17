import unittest

from ipo.app import build_app


class TestIpo(unittest.TestCase):
    def test_undersubscribed(self):
        api = build_app()
        api.create("ACME", 10_000)
        api.submit("ACME", {"investor": "r1", "shares": 500, "limit": "21"})
        api.submit("ACME", {"investor": "i1", "shares": 3_000, "limit": "21"})
        status, body = api.close("ACME", "20")
        self.assertEqual(status, 200)
        self.assertEqual(body["allocations"], {"i1": 3_000, "r1": 500})


if __name__ == "__main__":
    unittest.main()
