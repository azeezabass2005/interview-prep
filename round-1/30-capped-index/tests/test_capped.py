import unittest
from decimal import Decimal

from capped import IndexCalculator, Stock


def stock(ticker, size, free_float="1.0", price="10"):
    return Stock(ticker, int(size * 100_000_000), Decimal(free_float), Decimal(price))


class TestCapped(unittest.TestCase):
    def test_two_equal_stocks(self):
        result = IndexCalculator("0.6").rebalance([stock("A", 10), stock("B", 10)])
        self.assertEqual(result["weights"], {"A": Decimal("50.0000"), "B": Decimal("50.0000")})


if __name__ == "__main__":
    unittest.main()
