import unittest

from league.app import build_app


class TestLeague(unittest.TestCase):
    def test_points_order(self):
        api = build_app()
        api.teams("A", "B", "C")
        api.schedule("f1", "A", "B", "2026-03-01")
        api.schedule("f2", "C", "A", "2026-03-08")
        api.result("f1", 2, 0)
        api.result("f2", 0, 0)
        self.assertEqual([r["team"] for r in api.table()[1]["table"]], ["A", "C", "B"])


if __name__ == "__main__":
    unittest.main()
