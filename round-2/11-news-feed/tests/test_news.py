import unittest

from newsfeed.services.urls import canonical_url
from tests.helpers import World


class TestUrls(unittest.TestCase):
    def test_drops_tracking_params(self):
        self.assertEqual(canonical_url("https://partner.example/a?utm_source=x&id=3"), "https://partner.example/a?id=3")

    def test_sorts_query(self):
        self.assertEqual(canonical_url("https://p.example/a?b=2&a=1"), "https://p.example/a?a=1&b=2")


class TestFeed(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_ingest_and_duplicate(self):
        self.assertEqual(self.w.post(1).status, 201)
        self.assertEqual(self.w.post(1).body, {"duplicate": True})

    def test_feed_newest_first_and_pages(self):
        for n in range(1, 6):
            self.w.post(n)
        page1 = self.w.api.get_feed(limit=2).body
        page2 = self.w.api.get_feed(cursor=page1["next_cursor"], limit=2).body
        self.assertEqual([s["headline"] for s in page1["stories"] + page2["stories"]], ["S5", "S4", "S3", "S2"])

    def test_top_prefers_heavier_source_at_same_age(self):
        self.w.post(1, minutes_ago=30, source="blog")
        self.w.post(2, minutes_ago=30, source="wire-a")
        self.assertEqual(self.w.api.get_top().body["stories"][0]["headline"], "S2")

    def test_tag_search(self):
        self.w.post(1, tags=["fed"])
        self.w.post(2, tags=["ecb"])
        self.assertEqual([s["headline"] for s in self.w.api.get_tag("fed").body["stories"]], ["S1"])


if __name__ == "__main__":
    unittest.main()
