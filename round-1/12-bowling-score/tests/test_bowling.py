import unittest

from bowling.game import BowlingError, Game


def play(*rolls):
    game = Game()
    for pins in rolls:
        game.roll(pins)
    return game


class TestScoring(unittest.TestCase):
    def test_gutter_game(self):
        self.assertEqual(play(*[0] * 20).score(), 0)

    def test_all_ones(self):
        self.assertEqual(play(*[1] * 20).score(), 20)

    def test_one_spare(self):
        self.assertEqual(play(5, 5, 3, *[0] * 17).score(), 16)

    def test_one_strike(self):
        self.assertEqual(play(10, 3, 4, *[0] * 16).score(), 24)

    def test_running_totals(self):
        game = play(10, 3, 4, *[0] * 16)
        self.assertEqual(game.frame_scores()[:3], [17, 24, 24])


class TestValidation(unittest.TestCase):
    def test_pins_out_of_range(self):
        with self.assertRaises(BowlingError):
            play(11)
        with self.assertRaises(BowlingError):
            play(-1)

    def test_complete_after_twenty_open_rolls(self):
        self.assertTrue(play(*[0] * 20).is_complete())
        self.assertFalse(play(*[0] * 19).is_complete())


if __name__ == "__main__":
    unittest.main()
