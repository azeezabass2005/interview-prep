import unittest

from indexing.app import build_app

ON = "2026-06-19"


def index(cap, *secs):
    """secs: (ticker, size_in_100m, float, listed_on)"""
    api = build_app()
    api.define("I", cap)
    for ticker, size, flt, listed in secs:
        api.security(ticker, int(size * 100_000_000), flt, "10", listed)
    return api.rebalance("I", ON)[1]["weights"]


def s(ticker, size, flt="1.0", listed="2020-01-01"):
    return (ticker, size, flt, listed)


class HiddenIndex(unittest.TestCase):
    def test_B1_capping_repeats(self):
        w = index("0.25", s("A", 50), s("B", 20), s("C", 15), s("D", 10), s("E", 5))
        self.assertEqual(w, {"A": "25.0000", "B": "25.0000", "C": "25.0000", "D": "16.6667", "E": "8.3333"})

    def test_B2_proportional_redistribution(self):
        w = index("0.30", s("A", 40), s("B", 24), s("C", 24), s("D", 12))
        self.assertEqual(w, {"A": "30.0000", "B": "28.0000", "C": "28.0000", "D": "14.0000"})

    def test_B3_fifteen_percent_float_eligible(self):
        self.assertIn("F", index("1", s("A", 10), s("F", 10, flt="0.15")))

    def test_B4_float_adjusted(self):
        self.assertEqual(index("1", s("A", 10, "1.0"), s("B", 10, "0.5")), {"A": "66.6667", "B": "33.3333"})

    def test_B5_ninety_days_seasoning(self):
        self.assertIn("N", index("1", s("A", 10), s("N", 10, listed="2026-03-21")))
