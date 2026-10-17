import unittest

from orderbook import OrderBook


class TestOrderBook(unittest.TestCase):
    def test_partial_fill_of_resting_order(self):
        book = OrderBook()
        sell = book.submit("S1", "ann", "SELL", "9.90", 100)
        book.submit("B1", "bob", "BUY", "10.00", 40)
        self.assertEqual((sell.remaining, sell.status), (60, "PARTIAL"))


if __name__ == "__main__":
    unittest.main()
