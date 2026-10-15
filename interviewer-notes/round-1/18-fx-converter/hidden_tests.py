import unittest
from datetime import timedelta
from decimal import Decimal as D

from fx.convert import Converter
from fx.currencies import minor_units
from fx.rates import RateBook
from tests.helpers import FakeClock, standard_book


class HiddenFx(unittest.TestCase):
    def setUp(self):
        self.clock, book = standard_book()
        self.fx = Converter(book)

    def test_B1_usd_base_pairs_are_inverted(self):
        self.assertEqual(self.fx.quote(D("1512"), "JPY", "USD").target_amount, D("9.90"))

    def test_B2_spread_tier_uses_usd_equivalent(self):
        self.assertEqual(self.fx.quote(D("9000"), "GBP", "USD").target_amount, D("11372.85"))

    def test_B3_target_rounds_down(self):
        self.assertEqual(self.fx.quote(D("100"), "EUR", "USD").target_amount, D("107.41"))

    def test_B4_yen_has_no_decimals(self):
        self.assertEqual(minor_units("JPY"), 0)

    def test_G1_stale_rates_rejected(self):
        clock = FakeClock()
        book = RateBook(clock)
        book.set("EURUSD", "1.0850", at=clock.now() - timedelta(seconds=61))
        with self.assertRaises(Exception):
            Converter(book).quote(D("100"), "EUR", "USD")

    def test_spec_example(self):
        self.assertEqual(self.fx.quote(D("1000"), "EUR", "JPY").target_amount, D("162411"))
