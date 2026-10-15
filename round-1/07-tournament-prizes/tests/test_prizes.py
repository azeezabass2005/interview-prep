import unittest

from prizes.payouts import compute_payouts
from prizes.pool import payout_percentages, prize_pool, rake


def players(n):
    return [f"p{i:03d}" for i in range(1, n + 1)]


class TestPool(unittest.TestCase):
    def test_rake_is_ten_percent_of_fees(self):
        self.assertEqual(rake(100), 55_000)

    def test_large_field_pool(self):
        self.assertEqual(prize_pool(100), 495_000)

    def test_re_entries_count(self):
        entries = ["ana", "ben", "ana"]
        self.assertEqual(len(entries), 3)
        self.assertEqual(prize_pool(100) < prize_pool(101), True)

    def test_large_field_pays_five(self):
        self.assertEqual(payout_percentages(100), [40, 25, 15, 12, 8])


class TestPayouts(unittest.TestCase):
    def test_hundred_entries_no_ties(self):
        field = players(100)
        payouts = compute_payouts(field, [[p] for p in field])
        self.assertEqual(payouts["p001"], 198_000)
        self.assertEqual(len(payouts), 5)
        self.assertNotIn("p006", payouts)


if __name__ == "__main__":
    unittest.main()
