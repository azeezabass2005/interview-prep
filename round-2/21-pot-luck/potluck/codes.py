import random

from .config import CODE_LENGTH


class CodeGenerator:
    def __init__(self, rng=None):
        self._rng = rng or random.SystemRandom()

    def next_code(self) -> str:
        value = self._rng.randint(0, 10 ** CODE_LENGTH - 1)
        return str(value)
