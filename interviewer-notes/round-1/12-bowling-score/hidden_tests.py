import unittest

from bowling import League, frame_scores


class HiddenBowling(unittest.TestCase):
    def test_B1_spare_bonus_is_one_roll(self):
        self.assertEqual(frame_scores([5, 5, 3, 4] + [0] * 16)[:2], [13, 20])

    def test_B2_perfect_game_is_300(self):
        scores = frame_scores([10] * 12)
        self.assertEqual((len(scores), scores[-1]), (10, 300))

    def test_B3_strike_without_bonus_unknown(self):
        self.assertEqual(frame_scores([10, 3]), [None, None])

    def test_B4_handicap_never_negative(self):
        league = League()
        league.games["ana"] = [210]
        self.assertEqual(league.handicap("ana"), 0)

    def test_B5_handicap_from_previous_games(self):
        league = League()
        league.games["ana"] = [150]
        result = league.match("ana", [4] * 20, "ben", [3] * 20)
        self.assertEqual(result["ana"]["handicap"], 45)
