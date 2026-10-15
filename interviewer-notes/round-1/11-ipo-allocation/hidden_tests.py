import unittest

from ipo.allocation import allocate
from ipo.book import OrderBook


def book_with(offering, *orders):
    book = OrderBook(offering)
    for investor, shares in orders:
        book.submit(investor, shares)
    book.close()
    return book


class HiddenIpo(unittest.TestCase):
    def test_B1_guarantee_in_arrival_order(self):
        alloc = allocate(book_with(200, ("A", 300), ("B", 1_000), ("C", 500)))
        self.assertEqual(alloc, {"A": 100, "B": 100, "C": 0})

    def test_B2_spec_example(self):
        alloc = allocate(book_with(10_000, ("A", 8_000), ("B", 6_000), ("C", 1_000), ("D", 100)))
        self.assertEqual(alloc, {"A": 5_400, "B": 3_900, "C": 600, "D": 100})

    def test_B3_leftover_tie_goes_to_earliest(self):
        alloc = allocate(book_with(1_000, ("A", 1_000), ("B", 900)))
        self.assertEqual(alloc, {"A": 600, "B": 400})

    def test_G1_orders_must_be_whole_lots(self):
        with self.assertRaises(ValueError):
            OrderBook(1_000).submit("A", 150)

    def test_G2_no_orders_after_close(self):
        book = OrderBook(1_000)
        book.close()
        with self.assertRaises(Exception):
            book.submit("A", 100)
