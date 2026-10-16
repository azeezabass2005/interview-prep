import unittest

from league.app import build_app


def league(*results, teams=None):
    api = build_app()
    names = teams or sorted({t for r in results for t in r[:2]})
    api.teams(*names)
    for i, (home, away, hg, ag) in enumerate(results):
        api.schedule(f"f{i}", home, away, f"2026-03-{i + 1:02d}")
        api.result(f"f{i}", hg, ag)
    return api


def order(api):
    return [r["team"] for r in api.table()[1]["table"]]


class HiddenLeague(unittest.TestCase):
    def test_B1_away_conceded(self):
        row = {r["team"]: r for r in league(("A", "B", 2, 1)).table()[1]["table"]}["B"]
        self.assertEqual(row["gd"], -1)

    def test_B2_goal_difference_first(self):
        self.assertEqual(order(league(("X", "Z", 6, 1), ("Y", "W", 9, 6)))[:2], ["X", "Y"])

    def test_B3_head_to_head_among_tied(self):
        api = league(("Zeta", "Alpha", 1, 0), ("Cobras", "Zeta", 1, 0), ("Alpha", "Dynamo", 1, 0))
        self.assertEqual(order(api), ["Cobras", "Zeta", "Alpha", "Dynamo"])

    def test_B4_shared_positions(self):
        api = league(("A", "C", 1, 0), ("B", "D", 1, 0))
        self.assertEqual([r["pos"] for r in api.table()[1]["table"]], [1, 1, 3, 3])

    def test_B5_correction_replaces_result(self):
        api = league(("A", "B", 2, 0))
        api.result("f0", 0, 2)
        rows = {r["team"]: r for r in api.table()[1]["table"]}
        self.assertEqual((rows["B"]["pts"], rows["A"]["pts"], rows["A"]["played"]), (3, 0, 1))
