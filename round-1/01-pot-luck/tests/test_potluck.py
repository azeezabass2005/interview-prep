import unittest

from potluck import PotLuck
from tests.helpers import FakeRng


class TestPot(unittest.TestCase):
    def test_empty_draw_pot_is_sponsor_seed(self):
        game = PotLuck(rng=FakeRng([55555]))
        draw = game.close()
        self.assertEqual(draw.pot_cents, 1_000_000)

    def test_each_entry_adds_five_dollars(self):
        game = PotLuck(rng=FakeRng([11111, 22222]))
        game.add_entry("alice")
        game.add_entry("bob")
        self.assertEqual(game.current_pot_cents(), 1_001_000)

    def test_entry_requires_participant(self):
        game = PotLuck(rng=FakeRng([11111]))
        with self.assertRaises(ValueError):
            game.add_entry("")


class TestPayouts(unittest.TestCase):
    def test_single_four_match_gets_forty_percent(self):
        game = PotLuck(rng=FakeRng([12340, 12345]))
        entry = game.add_entry("alice")
        plan = game.settle(game.close())
        self.assertEqual(plan.amount_for(entry.entry_id), 1_000_500 * 40 // 100)

    def test_worked_example_from_spec(self):
        # 3 entries match 4 digits, 1 entry matches 2 digits; winning code 12345
        game = PotLuck(rng=FakeRng([12340, 12395, 92345, 12000, 12345]))
        four_a = game.add_entry("a")
        four_b = game.add_entry("b")
        four_c = game.add_entry("c")
        two = game.add_entry("d")
        plan = game.settle(game.close())

        self.assertEqual(plan.amount_for(four_a.entry_id), 133_600)
        self.assertEqual(plan.amount_for(four_b.entry_id), 133_600)
        self.assertEqual(plan.amount_for(four_c.entry_id), 133_600)
        self.assertEqual(plan.amount_for(two.entry_id), 50_100)
        self.assertEqual(plan.rollover_cents, 551_100)

    def test_no_winners_rolls_over_everything(self):
        game = PotLuck(rng=FakeRng([67890, 12345]))
        game.add_entry("alice")
        plan = game.settle(game.close())
        self.assertEqual(plan.payouts, [])
        self.assertEqual(plan.rollover_cents, 1_000_500)


if __name__ == "__main__":
    unittest.main()
