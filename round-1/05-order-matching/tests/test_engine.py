import unittest

from engine.matching import MatchingEngine
from engine.models import BUY, SELL, Fill, Order


class TestMatching(unittest.TestCase):
    def setUp(self):
        self.engine = MatchingEngine()

    def test_non_crossing_order_rests(self):
        self.assertEqual(self.engine.submit(Order("S1", "alice", SELL, 101, 10)), [])
        self.assertEqual(self.engine.book.asks.depth(), {101: 10})

    def test_full_fill_at_same_price(self):
        self.engine.submit(Order("S1", "alice", SELL, 100, 10))
        fills = self.engine.submit(Order("B1", "bob", BUY, 100, 10))
        self.assertEqual(fills, [Fill("B1", "S1", 100, 10)])
        self.assertEqual(self.engine.book.asks.depth(), {})

    def test_buy_walks_two_price_levels(self):
        self.engine.submit(Order("S1", "alice", SELL, 100, 10))
        self.engine.submit(Order("S2", "carol", SELL, 101, 10))
        fills = self.engine.submit(Order("B1", "bob", BUY, 101, 15))
        self.assertEqual([(f.resting_id, f.quantity) for f in fills], [("S1", 10), ("S2", 5)])
        self.assertEqual(self.engine.book.asks.depth(), {101: 5})

    def test_resting_partial_fill_keeps_remainder(self):
        self.engine.submit(Order("B1", "bob", BUY, 100, 50))
        self.engine.submit(Order("S1", "alice", SELL, 100, 20))
        self.assertEqual(self.engine.book.bids.depth(), {100: 30})

    def test_cancel(self):
        self.engine.submit(Order("S1", "alice", SELL, 101, 10))
        self.assertTrue(self.engine.cancel("S1"))
        self.assertFalse(self.engine.cancel("S1"))
        self.assertFalse(self.engine.cancel("nope"))

    def test_validation(self):
        with self.assertRaises(ValueError):
            Order("X", "alice", BUY, 100, 0)


if __name__ == "__main__":
    unittest.main()
