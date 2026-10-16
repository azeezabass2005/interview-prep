import unittest

from fees.app import build_app


class TestStatement(unittest.TestCase):
    def test_single_small_equity_buy(self):
        api, _ = build_app()
        api.open_account({"account_id": "ACC1", "owner": "Ann"})
        api.post_trade({"trade_id": "T1", "account_id": "ACC1", "asset_class": "EQUITY", "side": "BUY",
                        "quantity": 100, "price": "50.00", "executed_at": "2026-03-02T10:00:00"})
        status, body = api.statement("ACC1", 2026, 3)
        self.assertEqual(status, 200)
        self.assertEqual(body["total"], "5.00")


if __name__ == "__main__":
    unittest.main()
