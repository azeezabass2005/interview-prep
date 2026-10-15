import unittest

from ipo.allocation import allocate
from ipo.book import OrderBook


def book_with(offering, *orders):
    book = OrderBook(offering)
    for investor, shares in orders:
        book.submit(investor, shares)
    book.close()
    return book


class TestAllocation(unittest.TestCase):
    def test_undersubscribed_fills_everyone(self):
        alloc = allocate(book_with(10_000, ("A", 3_000), ("B", 2_000)))
        self.assertEqual(alloc, {"A": 3_000, "B": 2_000})

    def test_exactly_subscribed(self):
        alloc = allocate(book_with(1_000, ("A", 600), ("B", 400)))
        self.assertEqual(alloc, {"A": 600, "B": 400})

    def test_oversubscribed_allocates_whole_lots(self):
        alloc = allocate(book_with(1_000, ("A", 2_000), ("B", 2_000)))
        self.assertTrue(all(v % 100 == 0 for v in alloc.values()))
        self.assertEqual(sum(alloc.values()), 1_000)

    def test_duplicate_investor_rejected(self):
        book = OrderBook(1_000)
        book.submit("A", 100)
        with self.assertRaises(ValueError):
            book.submit("A", 200)

    def test_offering_must_be_whole_lots(self):
        with self.assertRaises(ValueError):
            OrderBook(1_050)


if __name__ == "__main__":
    unittest.main()
