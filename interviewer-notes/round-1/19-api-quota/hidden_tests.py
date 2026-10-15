import unittest
from decimal import Decimal as D

from tests.helpers import limiter_with


def drain(limiter, n, endpoint="/quote"):
    for _ in range(n):
        limiter.check("c1", endpoint)


class HiddenQuota(unittest.TestCase):
    def test_B1_refill_capped_at_capacity(self):
        clock, limiter = limiter_with("FREE")
        drain(limiter, 10)
        clock.at(100)
        results = [limiter.check("c1", "/quote").allowed for _ in range(11)]
        self.assertEqual(results, [True] * 10 + [False])

    def test_B2_downgrade_caps_tokens(self):
        _, limiter = limiter_with("PRO")
        limiter.change_plan("c1", "FREE")
        results = [limiter.check("c1", "/quote").allowed for _ in range(11)]
        self.assertEqual(results, [True] * 10 + [False])

    def test_B3_fractional_refill_accumulates(self):
        clock, limiter = limiter_with("FREE")
        drain(limiter, 10)
        clock.at("1.5")
        self.assertTrue(limiter.check("c1", "/quote").allowed)
        clock.at("2.0")
        self.assertTrue(limiter.check("c1", "/quote").allowed)

    def test_B4_retry_after_uses_refill_rate(self):
        _, limiter = limiter_with("PRO")
        drain(limiter, 5, "/bulk")
        decision = limiter.check("c1", "/bulk")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.retry_after, D("1.0"))

    def test_G1_impossible_request_has_no_retry(self):
        _, limiter = limiter_with("FREE")
        decision = limiter.check("c1", "/bulk")
        self.assertFalse(decision.allowed)
        self.assertIsNone(decision.retry_after)
