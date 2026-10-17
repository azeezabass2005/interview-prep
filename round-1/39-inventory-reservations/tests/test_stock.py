import unittest
from datetime import datetime

from stock import StockService

T0 = datetime(2026, 11, 27, 9, 0)


class TestStock(unittest.TestCase):
    def test_reservation_reduces_available(self):
        s = StockService()
        s.restock("TV", 10)
        s.reserve("cartA", "TV", 4, T0)
        self.assertEqual(s.available("TV", T0), 6)


if __name__ == "__main__":
    unittest.main()
