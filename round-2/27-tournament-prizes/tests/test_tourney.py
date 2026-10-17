import unittest

from tourney.app import build_app


class TestTourney(unittest.TestCase):
    def test_heads_up(self):
        api, _ = build_app()
        api.create("t1")
        api.enter("t1", "ana")
        api.enter("t1", "ben")
        api.start("t1")
        api.eliminate("t1", {"hand": 7, "eliminated": ["ben"], "winners": ["ana"]})
        status, result = api.finish("t1")
        self.assertEqual(status, 200)
        self.assertEqual(result["winner"], "ana")
        self.assertEqual(result["bounties"], {"ana": 1000})


if __name__ == "__main__":
    unittest.main()
