import unittest

from league.models import Result
from league.table import build_rows, standings


def order(table):
    return [row.team for _, row in table]


class HiddenLeague(unittest.TestCase):
    def test_B1_away_team_conceded_home_goals(self):
        rows = build_rows([Result("A", "B", 2, 1)])
        self.assertEqual(rows["B"].goals_against, 2)
        self.assertEqual(rows["B"].goal_difference, -1)

    def test_B2_goal_difference_before_goals_scored(self):
        table = standings([Result("X", "Z", 6, 1), Result("Y", "W", 9, 6)])
        self.assertEqual(order(table)[:2], ["X", "Y"])

    def test_B3_head_to_head_among_tied_teams(self):
        results = [Result("Zeta", "Alpha", 1, 0), Result("Cobras", "Zeta", 1, 0), Result("Alpha", "Dynamo", 1, 0)]
        self.assertEqual(order(standings(results)), ["Cobras", "Zeta", "Alpha", "Dynamo"])

    def test_B4_level_teams_share_position(self):
        table = standings([Result("A", "C", 1, 0), Result("B", "D", 1, 0)])
        self.assertEqual([pos for pos, _ in table], [1, 1, 3, 3])

    def test_G1_points_deductions_apply(self):
        table = standings([Result("A", "C", 1, 0), Result("B", "C", 0, 0)], deductions={"A": 3})
        self.assertEqual(order(table)[0], "B")
