"""Hidden grading tests. Each test fails on the original code for exactly one planted issue."""
import unittest

from potluck import PotLuck
from tests.helpers import FakeRng


class HiddenPotLuck(unittest.TestCase):
    def test_B1_codes_are_zero_padded(self):
        game = PotLuck(rng=FakeRng([42, 99999]))
        self.assertEqual(game.add_entry("a").code, "00042")
        self.assertEqual(game.add_entry("b").code, "99999")

    def test_B2_matching_is_positional(self):
        game = PotLuck(rng=FakeRng([54321, 12345]))
        entry = game.add_entry("a")
        plan = game.settle(game.close())
        self.assertEqual(plan.amount_for(entry.entry_id), 0)  # 1 positional match -> no payout

    def test_B3_five_match_claims_everything_first(self):
        game = PotLuck(rng=FakeRng([12345, 12340, 12345]))
        five = game.add_entry("a")
        four = game.add_entry("b")
        plan = game.settle(game.close())
        self.assertEqual(plan.amount_for(five.entry_id), 1_001_000)
        self.assertEqual(plan.amount_for(four.entry_id), 0)

    def test_B4_rollover_feeds_next_pot(self):
        game = PotLuck(rng=FakeRng([67890, 12345, 55555]))
        game.add_entry("a")
        game.settle(game.close())  # no winners: 1,000,500 rolls over
        game.start_next_draw()
        draw2 = game.close()
        self.assertEqual(draw2.pot_cents, 1_000_000 + 1_000_500)

    def test_B5_closed_draw_survives_next_draw(self):
        game = PotLuck(rng=FakeRng([12340, 12345]))
        entry = game.add_entry("a")
        draw = game.close()
        game.start_next_draw()
        self.assertEqual(len(draw.entries), 1)
        plan = game.settle(draw)
        self.assertGreater(plan.amount_for(entry.entry_id), 0)

    def test_G1_entries_rejected_after_close(self):
        game = PotLuck(rng=FakeRng([11111, 22222, 33333]))
        game.add_entry("a")
        game.close()
        with self.assertRaises(Exception):
            game.add_entry("late")
