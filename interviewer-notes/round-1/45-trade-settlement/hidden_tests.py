import unittest
from datetime import date

from settlement import Settlement

MON, TUE, WED = date(2026, 6, 29), date(2026, 6, 30), date(2026, 7, 1)


class HiddenSettlement(unittest.TestCase):
    def test_B1_holidays_skipped(self):
        s = Settlement(holidays=[date(2026, 7, 3)])
        self.assertEqual(s.settle_date(date(2026, 7, 2)), date(2026, 7, 6))

    def test_B2_sells_net_against_buys(self):
        s = Settlement()
        s.book("t1", "ana", "AAPL", "BUY", 100, "200", MON)
        s.book("t2", "ana", "AAPL", "SELL", 40, "201", MON)
        [ins] = s.net(TUE)
        self.assertEqual(ins.quantity, 60)

    def test_B3_cancelled_trades_excluded(self):
        s = Settlement()
        s.book("t1", "ana", "AAPL", "BUY", 100, "200", MON)
        s.book("t2", "ana", "AAPL", "BUY", 100, "200", MON)
        s.cancel("t2")
        [ins] = s.net(TUE)
        self.assertEqual(ins.quantity, 100)

    def test_B4_failed_instruction_retried_next_run(self):
        s = Settlement()
        s.book("t1", "ana", "AAPL", "SELL", 100, "200", MON)
        [first] = s.run(TUE, holdings={})
        first_status = first.status
        retried = s.run(WED, holdings={("ana", "AAPL"): 100})
        self.assertEqual((first_status, [(i.symbol, i.status) for i in retried]), ("FAILED", [("AAPL", "SETTLED")]))

    def test_B5_custodian_only_positions_are_breaks(self):
        breaks = Settlement.reconcile({"AAPL": 100}, {"AAPL": 100, "MSFT": 50})
        self.assertEqual(breaks, {"MSFT": (0, 50)})
