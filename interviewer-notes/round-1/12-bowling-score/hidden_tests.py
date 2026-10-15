import unittest

from bowling.game import Game


def play(*rolls):
    game = Game()
    for pins in rolls:
        game.roll(pins)
    return game


class HiddenBowling(unittest.TestCase):
    def test_B1_strike_bonus_spans_frames(self):
        game = play(10, 10, 5, 3, *[0] * 14)
        self.assertEqual(game.frame_scores()[0], 25)
        self.assertEqual(game.score(), 51)

    def test_B2_bonus_rolls_are_not_frames(self):
        self.assertEqual(play(*[5] * 21).score(), 150)

    def test_B3_frame_cannot_exceed_ten_pins(self):
        game = play(5)
        with self.assertRaises(Exception):
            game.roll(6)

    def test_B4_no_rolls_after_game_over(self):
        game = play(*[0] * 20)
        with self.assertRaises(Exception):
            game.roll(0)

    def test_B5_pending_strike_has_no_total(self):
        self.assertEqual(play(10).frame_scores(), [None])
        self.assertEqual(play(3, 4, 10, 2).frame_scores(), [7, None, None])

    def test_perfect_game(self):
        self.assertEqual(play(*[10] * 12).score(), 300)
