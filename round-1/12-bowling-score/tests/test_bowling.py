import unittest

from bowling import frame_scores


class TestBowling(unittest.TestCase):
    def test_open_frames(self):
        self.assertEqual(frame_scores([3, 4] * 10)[-1], 70)


if __name__ == "__main__":
    unittest.main()
