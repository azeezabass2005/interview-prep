import unittest

from tests.helpers import World


class TradingTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def positions(self, token):
        return self.w.call("GET", "/positions", token).body["positions"]

    def test_book_updates_the_desk_position(self):
        resp = self.w.book(self.w.rita, quantity=300)
        self.assertEqual(resp.status, 201)
        self.assertEqual(resp.body["trade_date"], "2026-06-05")
        self.w.book(self.w.rob, side="sell", quantity=100)
        self.assertEqual(self.positions(self.w.rita), {"UST10Y": 200})

    def test_validation(self):
        self.assertEqual(self.w.book(self.w.rita, side="hold").status, 400)
        self.assertEqual(self.w.book(self.w.rita, cp="cp_nope").status, 400)
        self.assertEqual(self.w.book(self.w.rita, quantity=0).status, 400)

    def test_position_limit(self):
        self.w.book(self.w.rita, quantity=5_000)
        self.w.book(self.w.rita, quantity=5_000)
        self.assertEqual(self.w.book(self.w.rita, quantity=1).status, 409)

    def test_traders_only_see_their_own_desk(self):
        trade = self.w.book(self.w.felix, symbol="EURUSD").body
        self.assertEqual(self.w.call("GET", f"/trades/{trade['id']}", self.w.rita).status, 404)
        self.assertEqual(self.w.call("GET", f"/trades/{trade['id']}", self.w.carla).status, 200)

    def test_trader_amends_own_trade_only(self):
        mine = self.w.book(self.w.rita).body
        theirs = self.w.book(self.w.rob).body
        self.assertEqual(self.w.call("PATCH", f"/trades/{mine['id']}", self.w.rita, {"quantity": 150}).status, 200)
        self.assertEqual(self.w.call("PATCH", f"/trades/{theirs['id']}", self.w.rita, {"quantity": 150}).status, 403)
        self.assertEqual(self.positions(self.w.rita), {"UST10Y": 250})

    def test_desk_head_amends_desk_trades(self):
        trade = self.w.book(self.w.rob).body
        resp = self.w.call("PATCH", f"/trades/{trade['id']}", self.w.ray, {"price_cents": 9_900})
        self.assertEqual((resp.status, resp.body["price_cents"], resp.body["version"]), (200, 9_900, 2))

    def test_cancel_reverses_the_position(self):
        trade = self.w.book(self.w.rita, quantity=400).body
        self.assertEqual(self.w.call("POST", f"/trades/{trade['id']}/cancel", self.w.rita).status, 403)
        self.assertEqual(self.w.call("POST", f"/trades/{trade['id']}/cancel", self.w.ray).status, 200)
        self.assertEqual(self.positions(self.w.rita), {"UST10Y": 0})

    def test_desk_head_cannot_cancel_another_desk(self):
        trade = self.w.book(self.w.felix, symbol="EURUSD").body
        self.assertEqual(self.w.call("POST", f"/trades/{trade['id']}/cancel", self.w.ray).status, 403)
        self.assertEqual(self.w.call("POST", f"/trades/{trade['id']}/cancel", self.w.carla).status, 200)

    def test_audit_trail(self):
        trade = self.w.book(self.w.rita).body
        self.w.call("PATCH", f"/trades/{trade['id']}", self.w.rita, {"quantity": 120})
        entries = self.w.call("GET", f"/trades/{trade['id']}/audit", self.w.rita).body["entries"]
        self.assertEqual([e["action"] for e in entries], ["book", "amend"])


class BlotterTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_blotter_has_counterparty_names(self):
        self.w.book(self.w.rita, cp="cp_gs")
        self.w.book(self.w.rob, cp="cp_ms")
        trades = self.w.call("GET", "/blotter", self.w.rita).body["trades"]
        self.assertEqual([t["counterparty"] for t in trades], ["Goldfinch Securities", "Morrow Stanley"])

    def test_other_desks_blotter_is_compliance_only(self):
        self.w.book(self.w.felix, symbol="EURUSD")
        self.assertEqual(self.w.call("GET", "/blotter?desk=fx", self.w.rita).status, 403)
        self.assertEqual(len(self.w.call("GET", "/blotter?desk=fx", self.w.carla).body["trades"]), 1)

    def test_eod_snapshot(self):
        self.w.book(self.w.rita, quantity=700)
        self.w.c.eod.schedule()
        self.w.c.worker.run_pending()
        snap = self.w.call("GET", "/snapshots/2026-06-05", self.w.rita).body
        self.assertEqual(snap["positions"], {"UST10Y": 700})


if __name__ == "__main__":
    unittest.main()
