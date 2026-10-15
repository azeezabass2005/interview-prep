import unittest

from tests.helpers import limiter_with


class TestQuota(unittest.TestCase):
    def test_bucket_starts_full(self):
        _, limiter = limiter_with("FREE")
        results = [limiter.check("c1", "/quote").allowed for _ in range(11)]
        self.assertEqual(results, [True] * 10 + [False])

    def test_history_costs_five(self):
        _, limiter = limiter_with("FREE")
        self.assertTrue(limiter.check("c1", "/history").allowed)
        self.assertTrue(limiter.check("c1", "/history").allowed)
        self.assertFalse(limiter.check("c1", "/quote").allowed)

    def test_refills_after_a_second(self):
        clock, limiter = limiter_with("FREE")
        for _ in range(10):
            limiter.check("c1", "/quote")
        clock.at(1)
        self.assertTrue(limiter.check("c1", "/quote").allowed)

    def test_unknown_endpoint(self):
        _, limiter = limiter_with("FREE")
        with self.assertRaises(ValueError):
            limiter.check("c1", "/admin")

    def test_upgrade_keeps_tokens(self):
        clock, limiter = limiter_with("FREE")
        limiter.change_plan("c1", "PRO")
        self.assertTrue(limiter.check("c1", "/history").allowed)


if __name__ == "__main__":
    unittest.main()
