import unittest

from tests.helpers import MON, THU, TUE, World


class TestSettlement(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_equity_t_plus_one_midweek(self):
        self.w.trade("T1", TUE)
        self.assertEqual(self.w.api.get_settlement_date("T1").body["settle_date"], "2026-06-10")

    def test_equity_friday_settles_monday(self):
        from datetime import date
        self.w.trade("T1", date(2026, 6, 12))
        self.assertEqual(self.w.api.get_settlement_date("T1").body["settle_date"], "2026-06-15")

    def test_matching_confirm_no_break(self):
        self.w.trade("T1", MON)
        self.w.confirm("T1", "101.25")
        self.assertEqual(self.w.api.get_breaks().body["breaks"], [])

    def test_quantity_break_and_missing_confirm(self):
        self.w.trade("T1", MON)
        self.w.trade("T2", MON)
        self.w.confirm("T1", "101.25", qty=90)
        types = sorted(b["type"] for b in self.w.api.get_breaks().body["breaks"])
        self.assertEqual(types, ["MISSING_CONFIRM", "QTY_OR_SIDE"])

    def test_netting_same_day(self):
        self.w.trade("T1", THU, side="BUY", qty=100, price="10")
        self.w.trade("T2", THU, side="SELL", qty=30, price="11")
        self.w.api.post_run_instructions()
        [instruction] = self.w.api.get_instructions().body["instructions"]
        self.assertEqual((instruction["net_quantity"], instruction["net_cash"]), (70, "-670"))


if __name__ == "__main__":
    unittest.main()
