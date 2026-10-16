import unittest

from fees.app import build_app


def app():
    api, store = build_app()
    api.open_account({"account_id": "A", "owner": "Ann"})
    return api


def trade(api, tid, notional_qty=100, price="50.00", side="BUY", asset="EQUITY", at="2026-03-02T10:00:00"):
    status, body = api.post_trade({"trade_id": tid, "account_id": "A", "asset_class": asset, "side": side,
                                   "quantity": notional_qty, "price": price, "executed_at": at})
    assert status == 201, body


def line(api, tid, year=2026, month=3):
    return next(l for l in api.statement("A", year, month)[1]["lines"] if l["trade_id"] == tid)


class HiddenFees(unittest.TestCase):
    def test_B1_marginal_tiers(self):
        api = app()
        trade(api, "T1", 600, "100.00")
        self.assertEqual(line(api, "T1")["commission"], "32.00")

    def test_B2_reg_fee_rounds_up(self):
        api = app()
        trade(api, "T1", 120, "100.00", side="SELL")
        self.assertEqual(line(api, "T1")["reg_fee"], "0.34")

    def test_B3_busted_trades_do_not_count_towards_discount(self):
        api = app()
        for i in range(1, 52):
            trade(api, f"T{i:02d}", at=f"2026-03-{(i % 20) + 2:02d}T10:{i:02d}:00")
        statement = api.statement("A", 2026, 3)[1]["lines"]
        first_id = statement[0]["trade_id"]
        api.bust_trade(first_id)
        lines = api.statement("A", 2026, 3)[1]["lines"]
        self.assertEqual(len(lines), 50)
        self.assertTrue(all(l["discount"] == "0.00" for l in lines))

    def test_B4_month_window_excludes_next_month(self):
        api = app()
        trade(api, "T1", at="2026-04-01T00:30:00")
        self.assertEqual(api.statement("A", 2026, 3)[1]["lines"], [])
        self.assertEqual(len(api.statement("A", 2026, 4)[1]["lines"]), 1)

    def test_B5_options_have_no_maximum(self):
        api = app()
        trade(api, "O1", 100, "2.50", asset="OPTION")
        self.assertEqual(line(api, "O1")["commission"], "65.00")
