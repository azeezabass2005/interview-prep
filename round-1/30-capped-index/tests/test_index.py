import unittest
from decimal import Decimal as D

from index.weights import is_eligible, publish, raw_weights
from tests.helpers import sec


class TestEligibility(unittest.TestCase):
    def test_penny_stock_excluded(self):
        self.assertFalse(is_eligible(sec("P", 100, price="0.50")))

    def test_small_cap_excluded(self):
        self.assertFalse(is_eligible(sec("S", 0.4)))  # $400M

    def test_low_float_excluded(self):
        self.assertFalse(is_eligible(sec("F", 10, free_float="0.10")))


class TestWeights(unittest.TestCase):
    def test_raw_weights_proportional(self):
        w = raw_weights([sec("A", 3), sec("B", 1)])
        self.assertEqual(w, {"A": D("0.75"), "B": D("0.25")})

    def test_no_capping_needed(self):
        self.assertEqual(publish([sec("A", 1), sec("B", 1)], cap=D("0.60")), {"A": D("50.0000"), "B": D("50.0000")})


if __name__ == "__main__":
    unittest.main()
