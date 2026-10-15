import unittest
from datetime import timedelta

from newsfeed.models import Story
from newsfeed.services.ranking import score
from tests.helpers import NOW, World


class HiddenNews(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_NEWS1101_url_variants_are_one_story(self):
        for url in ("https://www.partner.example/markets/fed-holds?utm_source=x",
                    "https://partner.example/markets/fed-holds/",
                    "HTTPS://Partner.example/markets/fed-holds#comments"):
            self.w.post(1, url=url)
        self.assertEqual(self.w.stories.count(), 1)
        self.w.post(2, url="https://partner.example/item?id=1")
        self.w.post(3, url="https://partner.example/item?id=2")
        self.assertEqual(self.w.stories.count(), 3)

    def test_NEWS1102_cursor_survives_new_arrivals(self):
        for n in range(1, 11):
            self.w.post(n)
        page1 = self.w.api.get_feed(limit=4).body
        self.w.post(11, minutes_ago=0)
        self.w.post(12, minutes_ago=0)
        page2 = self.w.api.get_feed(cursor=page1["next_cursor"], limit=4).body
        self.assertEqual([s["headline"] for s in page1["stories"]], ["S10", "S9", "S8", "S7"])
        self.assertEqual([s["headline"] for s in page2["stories"]], ["S6", "S5", "S4", "S3"])

    def test_NEWS1103_score_halves_every_six_hours(self):
        fresh = Story(1, "u1", "u1", "h", "wire-a", NOW)
        day_old = Story(2, "u2", "u2", "h", "wire-a", NOW - timedelta(hours=24))
        self.assertAlmostEqual(score(day_old, NOW) / score(fresh, NOW), 1 / 16, places=6)

    def test_NEWS1104_tags_case_insensitive(self):
        self.w.post(1, tags=["Fed"])
        self.w.post(2, tags=["FED"])
        self.w.post(3, tags=["fed"])
        self.assertEqual(len(self.w.api.get_tag("fed").body["stories"]), 3)
        self.assertEqual(len(self.w.api.get_tag("FED").body["stories"]), 3)
