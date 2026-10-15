import unittest
from decimal import Decimal as D

from index.weights import is_eligible, publish
from tests.helpers import sec


class HiddenIndex(unittest.TestCase):
    def test_B1_capping_repeats_until_no_breach(self):
        securities = [sec("A", 50), sec("B", 20), sec("C", 15), sec("D", 10), sec("E", 5)]
        self.assertEqual(publish(securities, cap=D("0.25")), {
            "A": D("25.0000"), "B": D("25.0000"), "C": D("25.0000"), "D": D("16.6667"), "E": D("8.3333"),
        })

    def test_B2_excess_redistributed_proportionally(self):
        securities = [sec("A", 40), sec("B", 24), sec("C", 24), sec("D", 12)]
        self.assertEqual(publish(securities, cap=D("0.30")), {
            "A": D("30.0000"), "B": D("28.0000"), "C": D("28.0000"), "D": D("14.0000"),
        })

    def test_B3_fifteen_percent_float_is_eligible(self):
        self.assertTrue(is_eligible(sec("F", 10, free_float="0.15")))

    def test_B4_weights_use_free_float(self):
        weights = publish([sec("A", 10, free_float="1.0"), sec("B", 10, free_float="0.5")], cap=D("1"))
        self.assertEqual(weights, {"A": D("66.6667"), "B": D("33.3333")})

    def test_B5_published_weights_sum_to_100(self):
        weights = publish([sec("A", 10), sec("B", 10), sec("C", 10)], cap=D("0.5"))
        self.assertEqual(sum(weights.values()), D("100.0000"))
