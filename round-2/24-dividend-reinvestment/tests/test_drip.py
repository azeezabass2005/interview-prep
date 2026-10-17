import unittest

from drip.app import build_app


class TestDrip(unittest.TestCase):
    def test_us_cash_holder(self):
        api, _ = build_app()
        api.open_account({"account_id": "A1", "name": "Ann", "country": "US"})
        api.record_movement({"account_id": "A1", "security": "BBG", "on": "2026-01-05", "shares": "100"})
        api.declare({"event_id": "Q1", "security": "BBG", "record_date": "2026-03-10", "pay_date": "2026-03-31",
                     "per_share": "0.82", "reinvest_price": "40.00"})
        status, body = api.process("Q1")
        self.assertEqual(status, 200)
        self.assertEqual(body["payments"][0]["cash_paid"], "82.00")


if __name__ == "__main__":
    unittest.main()
