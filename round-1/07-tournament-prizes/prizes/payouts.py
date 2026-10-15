from typing import Dict, List, Sequence

from .pool import payout_percentages, prize_pool


def place_amounts(entry_count: int) -> List[int]:
    pool = prize_pool(entry_count)
    return [pool * pct // 100 for pct in payout_percentages(entry_count)]


def compute_payouts(entries: Sequence[str], standings: Sequence[Sequence[str]]) -> Dict[str, int]:
    """
    entries:   one name per entry (re-entries appear more than once)
    standings: finishing groups, best first; a group of several names is a tie
    returns:   player -> prize in cents, for paid players only
    """
    amounts = place_amounts(len(entries))
    payouts: Dict[str, int] = {}
    place = 0
    for group in standings:
        if place >= len(amounts):
            break
        for player in sorted(group):
            payouts[player] = amounts[place]
        place += 1
    return payouts
