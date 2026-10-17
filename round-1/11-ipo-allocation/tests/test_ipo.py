import unittest

from ipo import OrderBook


class TestIpo(unittest.TestCase):
    def test_small_retail_order_filled(self):
        book = OrderBook(1000)
        book.place("r1", "ana", "RETAIL", 100)
        self.assertEqual(book.allocate("20.00")["r1"], 100)


if __name__ == "__main__":
    unittest.main()
