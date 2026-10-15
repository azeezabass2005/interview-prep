import re

from ..config import BANNED_WORDS

_PATTERN = re.compile(r"\b(" + "|".join(sorted(BANNED_WORDS)) + r")\b", re.IGNORECASE)


def mask(body: str) -> str:
    return _PATTERN.sub(lambda m: "*" * len(m.group(0)), body)
