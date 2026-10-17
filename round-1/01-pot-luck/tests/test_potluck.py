import unittest
from decimal import Decimal

from potluck import PotLuck


class Script:
    def __init__(self, *values):
        self.values = list(values)

    def randint(self, low, high):
        return self.values.pop(0)


class TestPotLuck(unittest.TestCase):
    def test_pot_includes_entries(self):
        game = PotLuck(Script(11111, 22222, 33333, 12345))
        game.register("ann", "ann@example.com")
        game.open_draw()
        game.buy("ann", 3)
        game.close()
        self.assertEqual(game.current.pot, Decimal("10015"))


if __name__ == "__main__":
    unittest.main()
