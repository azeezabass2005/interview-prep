import unittest

from blike.services.scoring import ScoringService


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.scoring = ScoringService()

    def test_internal_normal(self):
        self.assertEqual(self.scoring.score("alex@bloomberg.example", "normal"), 30)

    def test_external_high(self):
        self.assertEqual(self.scoring.score("sales@vendor.example", "high"), 30)

    def test_vip_low(self):
        self.assertEqual(self.scoring.score("cfo@bloomberg.example", "low"), 50)


if __name__ == "__main__":
    unittest.main()
