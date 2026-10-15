import threading
import unittest
from datetime import datetime
from unittest import mock

from boxoffice.errors import SeatUnavailable
from boxoffice.repositories.seats import SeatRepository
from tests.helpers import World


class HiddenBoxOffice(unittest.TestCase):
    def tearDown(self):
        self.w.cleanup()

    def test_TIX601_only_one_customer_wins_a_seat(self):
        self.w = World()
        a, b = self.w.seat_service(), self.w.seat_service()
        barrier = threading.Barrier(2, timeout=3)
        original = SeatRepository.get
        calls = {"n": 0}
        lock = threading.Lock()

        def paused_get(repo, event_id, seat_id):
            result = original(repo, event_id, seat_id)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        outcomes = []

        def run(svc, who):
            try:
                svc.hold("ev1", ["A1"], who)
                outcomes.append(who)
            except SeatUnavailable:
                outcomes.append("unavailable")

        with mock.patch.object(SeatRepository, "get", paused_get):
            threads = [threading.Thread(target=run, args=(a, "ann")), threading.Thread(target=run, args=(b, "bob"))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(outcomes.count("unavailable"), 1)
        winner = [o for o in outcomes if o != "unavailable"][0]
        self.assertEqual(SeatRepository(self.w.db).get("ev1", "A1").held_by, winner)

    def test_TIX602_expired_hold_frees_seat_same_day(self):
        self.w = World()
        self.w.api.post_hold("ann", "ev1", {"seats": ["B3"]})
        self.w.clock.advance(11)
        self.assertEqual(self.w.api.post_hold("bob", "ev1", {"seats": ["B3"]}).status, 200)

    def test_TIX603_refund_window_uses_venue_time_zone(self):
        self.w = World(now=datetime(2026, 9, 8, 22, 0))  # 50 h before the show (UTC)
        self.w.api.post_hold("ann", "ev1", {"seats": ["A1"]})
        order_id = self.w.api.post_purchase("ann", "ev1", {"seats": ["A1"]}).body["order_id"]
        self.assertEqual(self.w.api.post_refund(order_id).body.get("refunded_cents"), 4500)
        self.w.clock.current = datetime(2026, 9, 9, 4, 0)  # 44 h before
        self.w.api.post_hold("bob", "ev1", {"seats": ["A2"]})
        late = self.w.api.post_purchase("bob", "ev1", {"seats": ["A2"]}).body["order_id"]
        self.assertEqual(self.w.api.post_refund(late).status, 409)

    def test_TIX604_fee_per_ticket(self):
        self.w = World()
        self.w.api.post_hold("ann", "ev1", {"seats": ["A1", "A2", "A3"]})
        body = self.w.api.post_purchase("ann", "ev1", {"seats": ["A1", "A2", "A3"]}).body
        self.assertEqual((body["fee_total_cents"], body["total_cents"]), (1050, 14550))
