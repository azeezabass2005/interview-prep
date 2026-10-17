from typing import List

from ..config import GUARANTEE_CENTS, PAYOUT_TABLE, PRIZE_SIDE_CENTS, RAKE_PERCENT


def prize_side(entry_count: int) -> int:
    return entry_count * PRIZE_SIDE_CENTS


def rake(entry_count: int) -> int:
    return prize_side(entry_count) * RAKE_PERCENT // 100


def prize_pool(entry_count: int) -> int:
    return max(prize_side(entry_count), GUARANTEE_CENTS) - rake(entry_count)


def percentages(entry_count: int) -> List[int]:
    for max_entries, table in PAYOUT_TABLE:
        if max_entries is None or entry_count < max_entries:
            return table
    raise AssertionError("payout table must end with an unbounded bracket")


def place_amounts(entry_count: int) -> List[int]:
    pool = prize_pool(entry_count)
    amounts = [pool * p // 100 for p in percentages(entry_count)]
    amounts[0] += pool - sum(amounts)
    return amounts
