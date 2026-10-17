import unittest
from datetime import date

from standings import League

D1, D2, D3 = date(2026, 3, 1), date(2026, 3, 8), date(2026, 3, 15)


def row(league, team):
    return next(r for r in league.table() if r.team == team)


class HiddenStandings(unittest.TestCase):
    def test_B1_away_goals_against(self):
        league = League(["A", "B"])
        league.record("m1", D1, "A", "B", 2, 1)
        self.assertEqual(row(league, "B").goal_difference, -1)

    def test_B2_goal_difference_before_goals_scored(self):
        league = League(["X", "Y", "P", "Q"])
        league.record("m1", D1, "X", "P", 3, 0)
        league.record("m2", D1, "Y", "Q", 4, 2)
        self.assertEqual([r.team for r in league.table()][:2], ["X", "Y"])

    def test_B3_correction_replaces_result(self):
        league = League(["A", "B"])
        league.record("m1", D1, "A", "B", 1, 0)
        league.record("m1", D1, "A", "B", 0, 1)
        self.assertEqual((row(league, "A").points, row(league, "B").points), (0, 3))

    def test_B4_deductions_affect_order(self):
        league = League(["A", "B", "C"])
        league.record("m1", D1, "A", "C", 1, 0)
        league.record("m2", D2, "A", "C", 1, 0)
        league.record("m3", D3, "B", "C", 1, 0)
        league.deduct("A", 4)
        self.assertEqual([r.team for r in league.table()][:2], ["B", "A"])

    def test_B5_form_most_recent_first(self):
        league = League(["A", "B"])
        league.record("m1", D1, "A", "B", 1, 0)
        league.record("m2", D2, "A", "B", 0, 1)
        league.record("m3", D3, "A", "B", 2, 2)
        self.assertEqual(league.form("A"), "DLW")
