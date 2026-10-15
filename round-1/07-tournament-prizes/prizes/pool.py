from typing import List

from .config import ENTRY_FEE_CENTS, GUARANTEE_CENTS, PAYOUT_TABLE, RAKE_PERCENT


def entry_fees(entry_count: int) -> int:
    return entry_count * ENTRY_FEE_CENTS


def rake(entry_count: int) -> int:
    return entry_fees(entry_count) * RAKE_PERCENT // 100


def prize_pool(entry_count: int) -> int:
    return max(entry_fees(entry_count), GUARANTEE_CENTS) - rake(entry_count)


def payout_percentages(entry_count: int) -> List[int]:
    for max_entries, percentages in PAYOUT_TABLE:
        if max_entries is None or entry_count < max_entries:
            return percentages
    raise AssertionError("payout table must end with an unbounded bracket")
