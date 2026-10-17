from typing import Dict, List

from ..models import Tournament
from .pool import place_amounts
from .play import split_evenly


def final_eliminations(t: Tournament) -> List[tuple]:
    last_hand = {}
    for record in t.eliminations:
        for player in record.eliminated:
            last_hand[player] = record.hand
    groups: Dict[int, List[str]] = {}
    for player, hand in last_hand.items():
        if player == t.winner:
            continue
        reentered_after = any(e.live for e in t.entries_for(player))
        if not reentered_after:
            groups.setdefault(hand, []).append(player)
    return sorted(groups.items(), reverse=True)


def compute_places(t: Tournament) -> Dict[str, int]:
    places = {t.winner: 1}
    next_place = 2
    for _, players in final_eliminations(t):
        for player in players:
            places[player] = next_place
        next_place += len(players)
    return places


def compute_prizes(t: Tournament) -> Dict[str, int]:
    amounts = place_amounts(len(t.entries))
    places = compute_places(t)
    by_place: Dict[int, List[str]] = {}
    for player, place in places.items():
        by_place.setdefault(place, []).append(player)
    prizes = {}
    for place, players in sorted(by_place.items()):
        covered = amounts[place - 1:place - 1 + len(players)]
        if not covered:
            continue
        for player in players:
            prizes[player] = covered[0]
    return prizes
