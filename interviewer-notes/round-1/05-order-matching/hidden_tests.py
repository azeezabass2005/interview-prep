import unittest

from engine.matching import MatchingEngine
from engine.models import BUY, SELL, Order


class HiddenEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MatchingEngine()

    def test_B1_fills_at_resting_price(self):
        self.engine.submit(Order("S1", "a", SELL, 101, 100))
        self.engine.submit(Order("S2", "b", SELL, 100, 50))
        self.engine.submit(Order("S3", "c", SELL, 100, 70))
        fills = self.engine.submit(Order("B1", "d", BUY, 101, 130))
        self.assertEqual(sorted(f.price for f in fills), [100, 100, 101])

    def test_B2_time_priority_within_level(self):
        self.engine.submit(Order("S1", "a", SELL, 100, 10))
        self.engine.submit(Order("S2", "b", SELL, 100, 10))
        fills = self.engine.submit(Order("B1", "d", BUY, 100, 10))
        self.assertEqual([f.resting_id for f in fills], ["S1"])

    def test_B3_incoming_remainder_rests(self):
        self.engine.submit(Order("S1", "a", SELL, 100, 100))
        self.engine.submit(Order("B1", "d", BUY, 100, 150))
        self.assertEqual(self.engine.book.bids.depth(), {100: 50})

    def test_B4_partial_fill_keeps_queue_position(self):
        self.engine.submit(Order("S1", "a", SELL, 100, 100))
        self.engine.submit(Order("S2", "b", SELL, 100, 100))
        first = self.engine.submit(Order("B1", "d", BUY, 100, 30))
        second = self.engine.submit(Order("B2", "d", BUY, 100, 30))
        self.assertEqual([f.resting_id for f in first + second], ["S1", "S1"])

    def test_B5_cancel_removes_empty_level(self):
        self.engine.submit(Order("S1", "a", SELL, 101, 10))
        self.engine.submit(Order("S2", "b", SELL, 102, 10))
        self.engine.cancel("S1")
        self.assertEqual(self.engine.book.asks.best_price(), 102)
        fills = self.engine.submit(Order("B1", "d", BUY, 102, 5))
        self.assertEqual([f.resting_id for f in fills], ["S2"])

    def test_G1_no_self_trade(self):
        self.engine.submit(Order("S1", "alice", SELL, 99, 10))
        self.engine.submit(Order("S2", "bob", SELL, 100, 10))
        fills = self.engine.submit(Order("B1", "alice", BUY, 100, 10))
        self.assertEqual([f.resting_id for f in fills], ["S2"])
        self.assertIn("S1", self.engine.book.resting)
        self.assertEqual(self.engine.book.asks.depth(), {99: 10})
