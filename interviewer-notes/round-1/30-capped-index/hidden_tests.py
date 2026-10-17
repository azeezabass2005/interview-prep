import unittest
from decimal import Decimal

from capped import IndexCalculator, Stock


def stock(ticker, size, free_float="1.0", price="10"):
    return Stock(ticker, int(size * 100_000_000), Decimal(free_float), Decimal(price))


def weights(cap, *stocks):
    return {t: str(v) for t, v in IndexCalculator(cap).rebalance(list(stocks))["weights"].items()}


class HiddenCapped(unittest.TestCase):
    def test_B1_capping_repeats(self):
        w = weights("0.25", stock("A", 50), stock("B", 20), stock("C", 15), stock("D", 10), stock("E", 5))
        self.assertEqual(w, {"A": "25.0000", "B": "25.0000", "C": "25.0000", "D": "16.6667", "E": "8.3333"})

    def test_B2_half_up_rounding(self):
        w = weights("1", stock("A", 1), stock("B", 1), stock("C", 1), stock("D", 3))
        self.assertEqual(w["A"], "16.6667")

    def test_B3_float_adjusted(self):
        self.assertEqual(weights("1", stock("A", 10, "1.0"), stock("B", 10, "0.5")), {"A": "66.6667", "B": "33.3333"})

    def test_B4_residue_to_largest_uncapped(self):
        w = weights("0.5", stock("A", 10), stock("B", 1), stock("C", 1), stock("D", 1))
        self.assertEqual(w["A"], "50.0000")

    def test_B5_turnover_counts_removed_stocks(self):
        calc = IndexCalculator("1")
        calc.rebalance([stock("A", 10), stock("B", 10)])
        result = calc.rebalance([stock("A", 10), stock("B", 10, price="0.50"), stock("C", 5, price="20")])
        self.assertEqual(result["turnover"], Decimal("50"))
