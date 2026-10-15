import unittest

from tests.helpers import World


class TestLinks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_create_generated_code(self):
        resp = self.w.api.post_link("ann", {"target_url": "https://www.bloomberg.example/a"})
        self.assertEqual(resp.status, 201)
        self.assertEqual(len(resp.body["code"]), 6)

    def test_redirect(self):
        code = self.w.api.post_link("ann", {"target_url": "https://www.bloomberg.example/a"}).body["code"]
        resp = self.w.api.get_redirect(code)
        self.assertEqual((resp.status, resp.headers["Location"]), (302, "https://www.bloomberg.example/a"))

    def test_alias_and_case_insensitive_redirect(self):
        self.w.api.post_link("mkt", {"target_url": "https://www.bloomberg.example/summer", "alias": "SummerSale"})
        self.assertEqual(self.w.api.get_redirect("summersale").headers["Location"], "https://www.bloomberg.example/summer")

    def test_same_alias_rejected(self):
        self.w.api.post_link("mkt", {"target_url": "https://www.bloomberg.example/x", "alias": "promo"})
        self.assertEqual(self.w.api.post_link("bob", {"target_url": "https://e.example", "alias": "promo"}).status, 409)

    def test_reserved_and_blocked(self):
        self.assertEqual(self.w.api.post_link("a", {"target_url": "https://e.example", "alias": "admin"}).status, 400)
        self.assertEqual(self.w.api.post_link("a", {"target_url": "https://x.malware.example/"}).status, 400)

    def test_clicks_counted(self):
        code = self.w.api.post_link("ann", {"target_url": "https://e.example"}).body["code"]
        for _ in range(3):
            self.w.api.get_redirect(code)
        self.assertEqual(self.w.api.get_info(code).body["clicks"], 3)

    def test_info_shows_expiry(self):
        code = self.w.api.post_link("ann", {"target_url": "https://e.example", "ttl_days": 7}).body["code"]
        self.w.clock.advance(days=8)
        self.assertTrue(self.w.api.get_info(code).body["expired"])

    def test_unknown_code(self):
        self.assertEqual(self.w.api.get_redirect("nope00").status, 404)


if __name__ == "__main__":
    unittest.main()
