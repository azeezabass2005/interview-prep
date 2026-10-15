import unittest
from datetime import date

from tests.helpers import MON, TUE, World


class HiddenSettlement(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_STL1501_business_days_skip_holidays_and_weekends(self):
        self.w.trade("B1", date(2026, 7, 2), asset="CORP_BOND")
        self.w.trade("B2", date(2026, 6, 12), asset="CORP_BOND")
        self.assertEqual(self.w.api.get_settlement_date("B1").body["settle_date"], "2026-07-07")
        self.assertEqual(self.w.api.get_settlement_date("B2").body["settle_date"], "2026-06-16")

    def test_STL1502_price_tolerance(self):
        self.w.trade("T1", MON)
        self.w.trade("T2", MON)
        self.w.confirm("T1", "101.250049")
        self.w.confirm("T2", "101.2502")
        breaks = self.w.api.get_breaks().body["breaks"]
        self.assertEqual([(b["type"], b["trade_id"]) for b in breaks], [("PRICE", "T2")])

    def test_STL1503_rerun_is_idempotent(self):
        self.w.trade("T1", MON)
        self.w.api.post_run_instructions()
        self.w.api.post_run_instructions()
        self.assertEqual(len(self.w.api.get_instructions().body["instructions"]), 1)
        self.w.trade("T2", TUE, security="MSFT")
        self.w.api.post_run_instructions()
        trades = sorted(t for i in self.w.api.get_instructions().body["instructions"] for t in i["trades"])
        self.assertEqual(trades, ["T1", "T2"])

    def test_STL1504_net_per_settlement_date(self):
        self.w.trade("T1", MON, side="BUY", qty=100)
        self.w.trade("T2", TUE, side="SELL", qty=40)
        self.w.api.post_run_instructions()
        got = sorted((i["settle_date"], i["net_quantity"]) for i in self.w.api.get_instructions().body["instructions"])
        self.assertEqual(got, [("2026-06-09", 100), ("2026-06-10", -40)])
