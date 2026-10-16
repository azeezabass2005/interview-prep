import unittest

from league.app import build_app


def score(rolls):
    api, _ = build_app()
    return api.score_game(rolls)


class HiddenLeague(unittest.TestCase):
    def test_B1_strike_bonus_uses_next_rolls(self):
        self.assertEqual(score([10, 10, 5, 3] + [0] * 14)[1]["score"], 51)
        self.assertEqual(score([10] * 12)[1]["score"], 300)

    def test_B2_bonus_rolls_are_not_a_frame(self):
        self.assertEqual(score([0] * 18 + [10, 3, 4])[1]["score"], 17)

    def test_B3_handicap_uses_previous_games_only(self):
        api, _ = build_app()
        api.add_bowler({"bowler_id": "a", "history": [150, 161, 170]})
        api.add_bowler({"bowler_id": "b", "history": [200, 200, 200]})
        api.add_team("H", ["a"])
        api.add_team("A", ["b"])
        open_game = [3, 4] * 10
        body = api.record_match({"week": 1, "home": "H", "away": "A",
                                 "rolls": {"a": [open_game] * 3, "b": [open_game] * 3}})[1]
        self.assertEqual(body["totals"]["H"], [106, 106, 106])

    def test_B4_ties_split_points(self):
        api, _ = build_app()
        api.add_bowler({"bowler_id": "a"})
        api.add_bowler({"bowler_id": "b"})
        api.add_team("H", ["a"])
        api.add_team("A", ["b"])
        game = [3, 4] * 10
        body = api.record_match({"week": 1, "home": "H", "away": "A", "rolls": {"a": [game] * 3, "b": [game] * 3}})[1]
        self.assertEqual(body["points"], {"H": 2.0, "A": 2.0})

    def test_B5_frame_cannot_exceed_ten(self):
        self.assertEqual(score([5, 6])[0], 400)
