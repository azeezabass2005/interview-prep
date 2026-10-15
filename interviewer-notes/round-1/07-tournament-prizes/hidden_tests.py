import unittest

from prizes.payouts import compute_payouts
from prizes.pool import prize_pool


def players(n):
    return [f"p{i:03d}" for i in range(1, n + 1)]


class HiddenPrizes(unittest.TestCase):
    def test_B1_guarantee_is_floor_after_rake(self):
        self.assertEqual(prize_pool(20), 200_000)

    def test_B2_ten_entries_pays_two(self):
        field = players(10)
        self.assertEqual(len(compute_payouts(field, [[p] for p in field])), 2)

    def test_B3_tied_players_split_combined_places(self):
        field = ["ana", "ben", "cy", "dee"] + players(16)
        payouts = compute_payouts(field, [["ana"], ["ben", "cy"], ["dee"]])
        pool = prize_pool(20)
        expected = (pool * 30 // 100 + pool * 20 // 100) // 2
        self.assertEqual(payouts["ben"], expected)
        self.assertEqual(payouts["cy"], expected)

    def test_B4_finisher_after_tie_is_placed_after_it(self):
        field = ["ana", "ben", "cy", "dee"] + players(16)
        payouts = compute_payouts(field, [["ana"], ["ben", "cy"], ["dee"]])
        self.assertEqual(payouts.get("dee", 0), 0)

    def test_B5_payouts_add_up_to_pool(self):
        field = players(61)
        payouts = compute_payouts(field, [[p] for p in field])
        self.assertEqual(sum(payouts.values()), 301_950)
        self.assertEqual(payouts["p001"], 120_781)
