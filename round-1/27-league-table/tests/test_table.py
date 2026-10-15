import unittest

from league.models import Result
from league.table import build_rows, standings


class TestRows(unittest.TestCase):
    def test_win_and_draw_points(self):
        rows = build_rows([Result("A", "B", 2, 0), Result("A", "C", 1, 1)])
        self.assertEqual(rows["A"].points, 4)
        self.assertEqual(rows["C"].points, 1)
        self.assertEqual(rows["B"].points, 0)

    def test_home_goal_difference(self):
        rows = build_rows([Result("A", "B", 3, 1)])
        self.assertEqual(rows["A"].goal_difference, 2)

    def test_postponed_ignored(self):
        rows = build_rows([Result("A", "B")])
        self.assertEqual(rows["A"].played, 0)


class TestStandings(unittest.TestCase):
    def test_points_order(self):
        table = standings([Result("A", "B", 2, 0), Result("C", "A", 0, 0)])
        self.assertEqual([row.team for _, row in table], ["A", "C", "B"])


if __name__ == "__main__":
    unittest.main()
