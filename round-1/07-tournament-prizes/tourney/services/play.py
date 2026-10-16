from ..config import BOUNTY_CENTS
from ..errors import Rejected
from ..models import FINISHED, RUNNING, Elimination, Tournament
from .registration import RegistrationService


def split_evenly(amount: int, names):
    names = sorted(names)
    base, leftover = divmod(amount, len(names))
    return {name: base + (1 if i < leftover else 0) for i, name in enumerate(names)}


class PlayService:
    def __init__(self, registration: RegistrationService):
        self._registration = registration

    def eliminate(self, tournament_id: str, hand: int, eliminated, winners) -> Elimination:
        t = self._registration.get(tournament_id)
        if t.status != RUNNING:
            raise Rejected("tournament is not running")
        eliminated = tuple(sorted(p.lower() for p in eliminated))
        winners = tuple(sorted(p.lower() for p in winners))
        live = set(t.live_players())
        if not eliminated or not set(eliminated) <= live or not set(winners) <= live or set(winners) & set(eliminated):
            raise Rejected("eliminated and winning players must be distinct live players")
        if t.eliminations and hand <= t.eliminations[-1].hand:
            raise Rejected("hands must be recorded in order")
        for player in eliminated:
            for entry in t.entries_for(player):
                entry.live = False
        for name, amount in split_evenly(BOUNTY_CENTS * len(eliminated), winners).items():
            t.bounties[name] = t.bounties.get(name, 0) + amount
        record = Elimination(hand, eliminated, winners)
        t.eliminations.append(record)
        return record

    def finish(self, tournament_id: str) -> Tournament:
        t = self._registration.get(tournament_id)
        live = t.live_players()
        if t.status != RUNNING or len(live) != 1:
            raise Rejected("exactly one live player is needed to finish")
        t.winner = live[0]
        t.status = FINISHED
        return t
