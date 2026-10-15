import random

from .config import CODE_ALPHABET, CODE_LENGTH

_rng = random.SystemRandom()


def generate_code() -> str:
    return "".join(_rng.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
