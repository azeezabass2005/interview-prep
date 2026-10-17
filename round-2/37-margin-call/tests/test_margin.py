import unittest

from margin.app import build_app


class TestMargin(unittest.TestCase):
    def test_well_collateralised(self):
        api = build_app()
        api.add_security("TLT", "BOND")
        api.price("TLT", "2026-06-01", "100")
        api.open_account("A", "-1000", {"TLT": 100})
        status, body = api.run("A", "2026-06-01")
        self.assertEqual(status, 200)
        self.assertIsNone(body["call"])


if __name__ == "__main__":
    unittest.main()
