import unittest
from decimal import Decimal

from potluck import PotLuck


class Script:
    def __init__(self, *values):
        self.values = list(values)

    def randint(self, low, high):
        return self.values.pop(0)


def play(codes, winning, buyers=1):
    game = PotLuck(Script(*codes, winning))
    for i in range(buyers):
        game.register(f"p{i}", f"p{i}@example.com")
    game.open_draw()
    for i, _ in enumerate(codes):
        game.buy(f"p{i % buyers}")
    game.close()
    return game, game.settle()


class HiddenPotLuck(unittest.TestCase):
    def test_B1_codes_keep_leading_zeros(self):
        game = PotLuck(Script(42))
        game.register("ann", "ann@example.com")
        game.open_draw()
        entry_id = game.buy("ann")[0]
        self.assertEqual(game.entries[entry_id].code, "00042")

    def test_B2_matching_is_positional(self):
        _, result = play([54321], 12345)
        self.assertEqual(result["payouts"], {})

    def test_B3_tier_capped_by_what_is_left(self):
        _, result = play([12345, 12340], 12345)
        self.assertEqual(result["payouts"].get(2, Decimal("0")), Decimal("0"))
        self.assertEqual(result["rollover"], Decimal("0"))

    def test_B4_cancelled_entries_free_up_the_limit(self):
        game = PotLuck(Script(*range(10000, 10011)))
        game.register("ann", "ann@example.com")
        game.open_draw()
        ids = game.buy("ann", 10)
        game.cancel(ids[0])
        self.assertEqual(len(game.buy("ann")), 1)

    def test_B5_split_rounds_down(self):
        _, result = play([12399, 12399, 12399, 67890, 67890, 67890], 12345, buyers=6)
        self.assertEqual(result["payouts"][1], Decimal("668.66"))
        self.assertEqual(result["rollover"], Decimal("8024.02"))
