import os
import subprocess
import sys
import unittest

from tests.helpers import World, user

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class HiddenFlags(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_FF1701_rollout_is_sticky_and_stable_across_processes(self):
        a, b = self.w.instance(), self.w.instance()
        a.admin.save_flag("new-dashboard", rollout_percent=20)
        for uid in ("user-1", "user-42", "user-99"):
            answers = {a.evaluator.is_enabled("new-dashboard", user(uid)) for _ in range(20)}
            answers |= {b.evaluator.is_enabled("new-dashboard", user(uid)) for _ in range(20)}
            self.assertEqual(len(answers), 1, uid)
        share = sum(a.evaluator.is_enabled("new-dashboard", user(f"u{i}")) for i in range(10_000)) / 10_000
        self.assertTrue(0.15 <= share <= 0.25, share)
        code = "from flags.services.bucketing import bucket; print(bucket('new-dashboard', 'user-42'))"
        outputs = {subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
                                  env={**os.environ, "PYTHONHASHSEED": seed}).stdout.strip() for seed in ("1", "2", "3")}
        self.assertEqual(len(outputs), 1, outputs)

    def test_FF1702_override_beats_segment_rule(self):
        app = self.w.instance()
        app.admin.save_flag("new-dashboard", rollout_percent=0)
        app.admin.add_rule("new-dashboard", 1, "country", "GB", True)
        app.admin.override("new-dashboard", "screen-reader-user", False)
        self.assertFalse(app.evaluator.is_enabled("new-dashboard", user("screen-reader-user", country="GB")))

    def test_FF1703_change_visible_immediately_locally_and_cache_still_used(self):
        a, b = self.w.instance(), self.w.instance()
        a.admin.save_flag("f", rollout_percent=100)
        self.assertTrue(a.evaluator.is_enabled("f", user("u1")))
        self.assertTrue(b.evaluator.is_enabled("f", user("u1")))
        a.admin.save_flag("f", enabled=False, rollout_percent=100)
        self.assertFalse(a.evaluator.is_enabled("f", user("u1")))
        loads_before = b.repo.loads
        for _ in range(100):
            b.evaluator.is_enabled("f", user("u1"))
        self.assertLessEqual(b.repo.loads - loads_before, 1)
        self.w.clock.advance(31)
        self.assertFalse(b.evaluator.is_enabled("f", user("u1")))

    def test_FF1704_archived_flag_uses_caller_default(self):
        app = self.w.instance()
        app.admin.save_flag("beta-export", rollout_percent=100)
        app.admin.archive("beta-export")
        app.cache.invalidate()
        self.assertFalse(app.evaluator.is_enabled("beta-export", user("u1"), default=False))
        self.assertTrue(app.evaluator.is_enabled("beta-export", user("u1"), default=True))
