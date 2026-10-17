import unittest

from loyalty.app import build_app


class TestLoyalty(unittest.TestCase):
    def test_base_member_earns(self):
        api, _ = build_app()
        api.join("m1", "Ann")
        status, body = api.fly({"flight_id": "F1", "member_id": "m1", "date": "2026-02-01", "fare": "100.00"})
        self.assertEqual(status, 201)
        self.assertEqual(api.account("m1", "2026-03-01")[1], {"balance": 500, "tier": "BASE"})


if __name__ == "__main__":
    unittest.main()
