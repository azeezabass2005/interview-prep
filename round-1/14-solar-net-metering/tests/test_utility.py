import unittest

from utility.app import build_app


class TestUtility(unittest.TestCase):
    def test_small_month(self):
        api = build_app()
        api.open({"account_id": "A", "read_on": "2026-03-01", "import": 1000, "export": 0})
        status, bill = api.read("A", {"read_on": "2026-03-31", "import": 1400, "export": 0})
        self.assertEqual(status, 201)
        self.assertEqual(bill["billable_kwh"], 400)


if __name__ == "__main__":
    unittest.main()
