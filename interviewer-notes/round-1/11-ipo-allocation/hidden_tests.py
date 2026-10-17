import unittest

from ipo import OrderBook


class HiddenIpo(unittest.TestCase):
    def test_B1_limit_equal_to_price_is_eligible(self):
        book = OrderBook(1000)
        book.place("a", "fund", "INSTITUTIONAL", 500, limit="20.00")
        self.assertEqual(book.allocate("20.00").get("a"), 500)

    def test_B2_amending_up_loses_priority(self):
        book = OrderBook(1000)
        book.place("r", "ana", "RETAIL", 200)
        book.place("a", "f1", "INSTITUTIONAL", 300)
        book.place("b", "f2", "INSTITUTIONAL", 200)
        book.place("c", "f3", "INSTITUTIONAL", 300)
        book.amend("b", shares=300)
        alloc = book.allocate("20")
        self.assertEqual((alloc["a"], alloc["b"], alloc["c"]), (267, 266, 267))

    def test_B3_spare_tranche_shares_move(self):
        book = OrderBook(1000)
        book.place("r", "ana", "RETAIL", 100)
        book.place("a", "fund", "INSTITUTIONAL", 900)
        self.assertEqual(book.allocate("20")["a"], 900)

    def test_B4_retail_in_lots_of_100(self):
        book = OrderBook(1000)
        book.place("r1", "ana", "RETAIL", 300)
        book.place("r2", "ben", "RETAIL", 100)
        book.place("a", "fund", "INSTITUTIONAL", 800)
        alloc = book.allocate("20")
        self.assertEqual((alloc["r1"], alloc["r2"]), (200, 0))

    def test_B5_cancelled_orders_excluded(self):
        book = OrderBook(1000)
        book.place("r", "ana", "RETAIL", 200)
        book.place("a", "f1", "INSTITUTIONAL", 900)
        book.place("b", "f2", "INSTITUTIONAL", 900)
        book.cancel("b")
        alloc = book.allocate("20")
        self.assertEqual((alloc["a"], alloc.get("b", 0)), (800, 0))
