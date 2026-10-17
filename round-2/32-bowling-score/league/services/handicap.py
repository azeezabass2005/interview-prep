from typing import List, Optional

BASE = 200
PERCENT = 90


def average(history: List[int]) -> Optional[int]:
    if not history:
        return None
    return sum(history) // len(history)


def handicap(history: List[int]) -> int:
    avg = average(history)
    if avg is None:
        return 0
    return max(0, (BASE - avg) * PERCENT // 100)
