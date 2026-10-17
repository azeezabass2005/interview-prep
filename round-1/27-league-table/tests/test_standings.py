import unittest
from datetime import date

from standings import League


class TestStandings(unittest.TestCase):
    def test_home_win_gives_three_points(self):
        league = League(["Ajax", "Bulls"])
        league.record("m1", date(2026, 3, 1), "Ajax", "Bulls", 2, 0)
        self.assertEqual([(r.team, r.points) for r in league.table()], [("Ajax", 3), ("Bulls", 0)])


if __name__ == "__main__":
    unittest.main()
