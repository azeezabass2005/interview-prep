import unittest
from datetime import datetime

from tests.helpers import World


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_blt401_desk_head_cannot_amend_another_desks_trade(self):
        trade = self.w.book(self.w.felix, symbol="EURUSD", quantity=200).body
        self.assertEqual(self.w.call("GET", f"/trades/{trade['id']}", self.w.ray).status, 200)
        resp = self.w.call("PATCH", f"/trades/{trade['id']}", self.w.ray, {"quantity": 900})
        self.assertEqual(resp.status, 403)
        self.assertEqual(self.w.call("GET", "/positions", self.w.felix).body["positions"], {"EURUSD": 200})
        self.assertEqual(self.w.call("PATCH", f"/trades/{trade['id']}", self.w.fay, {"quantity": 250}).status, 200)

    def test_blt405_limit_rejection_leaves_no_trace(self):
        self.w.book(self.w.rita, quantity=5_000)
        self.w.book(self.w.rita, quantity=4_500)
        self.assertEqual(self.w.book(self.w.rita, quantity=1_000).status, 409)
        trades = self.w.call("GET", "/blotter", self.w.rita).body["trades"]
        self.assertEqual([t["quantity"] for t in trades], [5_000, 4_500])
        self.assertEqual(self.w.call("GET", "/positions", self.w.rita).body["positions"], {"UST10Y": 9_500})

    def test_blt410_blotter_query_count_is_constant(self):
        for i in range(30):
            self.w.book(self.w.rita, quantity=10, cp=["cp_gs", "cp_ms", "cp_jp"][i % 3])
        before = len(self.w.db.statements)
        trades = self.w.call("GET", "/blotter", self.w.rita).body["trades"]
        self.assertEqual(len(trades), 30)
        self.assertEqual(trades[1]["counterparty"], "Morrow Stanley")
        self.assertLessEqual(len(self.w.db.statements) - before, 4)

    def test_blt415_snapshot_uses_the_new_york_business_date(self):
        self.w.book(self.w.rita, quantity=700)
        self.w.clock._now = datetime(2026, 6, 6, 1, 30)  # 21:30 Friday in New York
        self.w.c.eod.schedule()
        self.w.c.worker.run_pending()
        self.assertEqual(self.w.call("GET", "/snapshots/2026-06-05", self.w.rita).body["positions"], {"UST10Y": 700})
        self.assertEqual(self.w.call("GET", "/snapshots/2026-06-06", self.w.rita).body["positions"], {})

    def test_blt420_invalid_amendments_are_400(self):
        trade = self.w.book(self.w.rita).body
        zero = self.w.call("PATCH", f"/trades/{trade['id']}", self.w.rita, {"quantity": 0})
        self.assertEqual((zero.status, zero.body["error"]["code"]), (400, "validation_error"))
        self.assertEqual(self.w.call("PATCH", f"/trades/{trade['id']}", self.w.rita, {"price_cents": -5}).status, 400)
        self.assertEqual(self.w.call("PATCH", f"/trades/{trade['id']}", self.w.rita, {"quantity": 120}).status, 200)


if __name__ == "__main__":
    unittest.main()
