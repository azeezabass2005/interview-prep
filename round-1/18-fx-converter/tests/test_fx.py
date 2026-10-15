import unittest
from decimal import Decimal as D

from fx.convert import Converter, spread_for
from tests.helpers import standard_book


class TestSpread(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(spread_for(D("500")), D("0.0100"))
        self.assertEqual(spread_for(D("10000")), D("0.0050"))
        self.assertEqual(spread_for(D("250000")), D("0.0025"))


class TestQuotes(unittest.TestCase):
    def setUp(self):
        _, book = standard_book()
        self.fx = Converter(book)

    def test_eur_to_usd(self):
        self.assertEqual(self.fx.quote(D("1000"), "EUR", "USD").target_amount, D("1074.15"))

    def test_gbp_to_eur_cross(self):
        q = self.fx.quote(D("1000"), "GBP", "EUR")
        self.assertEqual(q.target_amount, D("1158.80"))  # 1270 / 1.085 = 1170.5069... × 0.99

    def test_rejects_non_positive(self):
        with self.assertRaises(ValueError):
            self.fx.quote(D("0"), "EUR", "USD")

    def test_unknown_currency(self):
        with self.assertRaises(KeyError):
            self.fx.quote(D("10"), "EUR", "BRL")


if __name__ == "__main__":
    unittest.main()
