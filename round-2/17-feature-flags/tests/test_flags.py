import unittest

from tests.helpers import World, user


class TestFlags(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.app = self.w.instance()

    def tearDown(self):
        self.w.cleanup()

    def test_unknown_flag_uses_default(self):
        self.assertTrue(self.app.evaluator.is_enabled("nope", user("u1"), default=True))
        self.assertFalse(self.app.evaluator.is_enabled("nope", user("u1")))

    def test_fully_rolled_out(self):
        self.app.admin.save_flag("f", rollout_percent=100)
        self.assertTrue(self.app.evaluator.is_enabled("f", user("u1")))

    def test_disabled_flag_is_off(self):
        self.app.admin.save_flag("f", enabled=False, rollout_percent=100)
        self.assertFalse(self.app.evaluator.is_enabled("f", user("u1")))

    def test_segment_rule(self):
        self.app.admin.save_flag("f", rollout_percent=0)
        self.app.admin.add_rule("f", 1, "country", "GB", True)
        self.assertTrue(self.app.evaluator.is_enabled("f", user("u1", country="GB")))
        self.assertFalse(self.app.evaluator.is_enabled("f", user("u2", country="US")))

    def test_override_on(self):
        self.app.admin.save_flag("f", rollout_percent=0)
        self.app.admin.override("f", "vip", True)
        self.assertTrue(self.app.evaluator.is_enabled("f", user("vip")))

    def test_rollout_percent_validation(self):
        with self.assertRaises(ValueError):
            self.app.admin.save_flag("f", rollout_percent=101)


if __name__ == "__main__":
    unittest.main()
