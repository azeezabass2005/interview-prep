import unittest
from datetime import datetime
from decimal import Decimal

from leaderboard import Leaderboard


def board_with(*people):
    board = Leaderboard()
    for i, (name, trades) in enumerate(people):
        board.join(name, datetime(2026, 6, 1, 9, i))
        for _ in range(trades):
            board.trade(name, "XYZ", "BUY", 1, "10")
    return board


class HiddenLeaderboard(unittest.TestCase):
    def test_B1_fewer_trades_win_ties(self):
        board = board_with(("ana", 7), ("ben", 6))
        self.assertEqual([name for _, name, _ in board.standings()], ["ben", "ana"])

    def test_B2_valued_at_market_price(self):
        board = board_with(("ana", 0))
        board.trade("ana", "XYZ", "BUY", 100, "10")
        board.set_price("XYZ", "12")
        self.assertEqual(board.value("ana"), Decimal("100200"))

    def test_B3_five_trades_qualify(self):
        self.assertEqual([name for _, name, _ in board_with(("ana", 5)).standings()], ["ana"])

    def test_B4_disqualified_hidden(self):
        board = board_with(("ana", 6), ("ben", 6))
        board.disqualify("ana")
        self.assertEqual([name for _, name, _ in board.standings()], ["ben"])

    def test_B5_first_page_is_page_one(self):
        board = board_with(("ana", 6), ("ben", 7), ("cai", 8))
        self.assertEqual([rank for rank, _, _ in board.page(1, size=2)], [1, 2])
