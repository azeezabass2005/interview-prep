import unittest

from tests.helpers import World


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.people("Ada", "Bo", "Cy")

    def tearDown(self):
        self.w.cleanup()

    def test_points_accumulate(self):
        self.w.api.post_points("ada", {"points": 50})
        self.assertEqual(self.w.api.post_points("ada", {"points": -20}).body["total"], 30)

    def test_invalid_points(self):
        self.assertEqual(self.w.api.post_points("ada", {"points": "lots"}).status, 400)

    def test_distinct_scores_ranked(self):
        self.w.api.post_points("ada", {"points": 300})
        self.w.api.post_points("bo", {"points": 200})
        self.w.api.post_points("cy", {"points": 100})
        self.assertEqual([(s["name"], s["rank"]) for s in self.w.api.get_page().body["standings"]],
                         [("Ada", 1), ("Bo", 2), ("Cy", 3)])

    def test_weekly_board_midweek(self):
        self.w.api.post_points("bo", {"points": 10})
        self.assertEqual(self.w.api.get_weekly().body["standings"][0]["name"], "Bo")


if __name__ == "__main__":
    unittest.main()
