import unittest
from datetime import datetime
from decimal import Decimal

from leaderboard import Leaderboard


class TestLeaderboard(unittest.TestCase):
    def test_buy_reduces_cash(self):
        board = Leaderboard()
        board.join("ana", datetime(2026, 6, 1, 9))
        board.trade("ana", "XYZ", "BUY", 100, "10")
        self.assertEqual(board.participants["ana"].cash, Decimal("99000"))


if __name__ == "__main__":
    unittest.main()
