import unittest
from decimal import Decimal

from orderbook import OrderBook


class HiddenOrderBook(unittest.TestCase):
    def test_B1_trades_at_resting_price(self):
        book = OrderBook()
        book.submit("S1", "ann", "SELL", "10.00", 100)
        book.submit("B1", "bob", "BUY", "10.50", 100)
        self.assertEqual(book.trades[0]["price"], Decimal("10.00"))

    def test_B2_earliest_order_first_at_same_price(self):
        book = OrderBook()
        book.submit("S1", "ann", "SELL", "10.00", 50)
        book.submit("S2", "cat", "SELL", "10.00", 50)
        book.submit("B1", "bob", "BUY", "10.10", 50)
        self.assertEqual(book.trades[0]["sell_id"], "S1")

    def test_B3_ioc_remainder_cancelled(self):
        book = OrderBook()
        book.submit("S1", "ann", "SELL", "10.00", 100)
        order = book.submit("B1", "bob", "BUY", "10.10", 150, "IOC")
        self.assertEqual((order.status, book.bids), ("CANCELLED", {}))

    def test_B4_equal_prices_trade(self):
        book = OrderBook()
        book.submit("S1", "ann", "SELL", "10.00", 100)
        book.submit("B1", "bob", "BUY", "10.00", 100)
        self.assertEqual(len(book.trades), 1)

    def test_B5_self_trade_prevention(self):
        book = OrderBook()
        book.submit("S1", "ann", "SELL", "10.00", 100)
        book.submit("S2", "cat", "SELL", "10.10", 100)
        book.submit("B1", "ann", "BUY", "10.20", 100)
        self.assertEqual([t["sell_id"] for t in book.trades], ["S2"])
        self.assertEqual(book.orders["S1"].status, "CANCELLED")
