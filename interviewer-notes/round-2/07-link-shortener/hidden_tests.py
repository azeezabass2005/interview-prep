import threading
import unittest
from unittest import mock

from shortlinks.repositories.links import LinkRepository
from tests.helpers import World


class HiddenLinks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_LNK701_alias_unique_ignoring_case(self):
        self.w.api.post_link("mkt", {"target_url": "https://www.bloomberg.example/summer", "alias": "SummerSale"})
        self.assertEqual(self.w.api.post_link("bob", {"target_url": "https://blog.example/me", "alias": "summersale"}).status, 409)
        self.assertEqual(self.w.api.get_redirect("SummerSale").headers["Location"], "https://www.bloomberg.example/summer")

    def test_LNK702_concurrent_clicks_all_counted(self):
        code = self.w.api.post_link("ann", {"target_url": "https://e.example"}).body["code"]
        a, b = self.w.instance(), self.w.instance()
        barrier = threading.Barrier(2, timeout=3)
        original = LinkRepository.lookup
        calls = {"n": 0}
        lock = threading.Lock()

        def paused(repo, c):
            result = original(repo, c)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        with mock.patch.object(LinkRepository, "lookup", paused):
            threads = [threading.Thread(target=s.resolve, args=(code,)) for s in (a, b)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(self.w.repo.get(code).clicks, 2)

    def test_LNK703_expired_link_is_gone(self):
        code = self.w.api.post_link("ann", {"target_url": "https://e.example/preview", "ttl_days": 7}).body["code"]
        self.w.clock.advance(days=8)
        self.assertEqual(self.w.api.get_redirect(code).status, 410)
        self.assertEqual(self.w.repo.click_event_count(code), 0)

    def test_LNK704_collision_never_overwrites(self):
        with mock.patch("shortlinks.services.links.generate_code", side_effect=["abc123", "abc123", "zzz999"]):
            first = self.w.api.post_link("ann", {"target_url": "https://clients.example/report"}).body["code"]
            second = self.w.api.post_link("bob", {"target_url": "https://intranet.example/survey"}).body["code"]
        self.assertEqual(first, "abc123")
        self.assertNotEqual(second, "abc123")
        self.assertEqual(self.w.repo.get("abc123").target_url, "https://clients.example/report")
