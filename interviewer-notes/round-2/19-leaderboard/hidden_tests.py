import threading
import unittest
from datetime import datetime
from unittest import mock

from board.repositories.scores import ScoreRepository
from tests.helpers import World


class HiddenBoard(unittest.TestCase):
    def tearDown(self):
        self.w.cleanup()

    def test_LB1901_concurrent_points_not_lost(self):
        self.w = World()
        self.w.people("Ada")
        a, b = self.w.scoring(), self.w.scoring()
        barrier = threading.Barrier(2, timeout=3)
        original = ScoreRepository.total
        calls = {"n": 0}
        lock = threading.Lock()

        def paused(repo, pid):
            result = original(repo, pid)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        with mock.patch.object(ScoreRepository, "total", paused):
            threads = [threading.Thread(target=svc.add_points, args=("ada", pts)) for svc, pts in ((a, 10), (b, 20))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(self.w.scores.total("ada"), 30)
        self.assertEqual(self.w.scores.total("ada"), self.w.scores.events_sum("ada"))

    def test_LB1902_competition_ranking(self):
        self.w = World()
        self.w.people("Ada", "Bo", "Cy", "Di")
        for pid, pts in (("ada", 500), ("bo", 400), ("cy", 400), ("di", 300)):
            self.w.api.post_points(pid, {"points": pts})
        self.assertEqual([s["rank"] for s in self.w.api.get_page(size=10).body["standings"]], [1, 2, 2, 4])

    def test_LB1903_ties_alphabetical_and_each_once(self):
        self.w = World()
        self.w.people("Zed", "Yan", "Xi", "Wu", "Val")
        names = []
        for page in (1, 2, 3):
            names += [s["name"] for s in self.w.api.get_page(page=page, size=2).body["standings"]]
        self.assertEqual(names, ["Val", "Wu", "Xi", "Yan", "Zed"])

    def test_LB1904_weeks_run_monday_to_sunday(self):
        self.w = World(now=datetime(2026, 6, 14, 18, 0))  # Sunday
        self.w.people("Ada", "Bo")
        self.w.api.post_points("ada", {"points": 50})
        self.assertEqual([s["name"] for s in self.w.api.get_weekly().body["standings"]], ["Ada"])
        self.w.clock.current = datetime(2026, 6, 15, 9, 0)  # Monday
        self.w.api.post_points("bo", {"points": 5})
        self.assertEqual([s["name"] for s in self.w.api.get_weekly().body["standings"]], ["Bo"])
