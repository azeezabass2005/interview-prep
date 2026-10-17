from ..config import LATE_REG_LAST_LEVEL, MAX_REENTRIES
from ..errors import NotFound, Rejected
from ..models import FINISHED, REGISTERING, RUNNING, Entry, Tournament
from ..store import InMemoryStore


class RegistrationService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def create(self, tournament_id: str) -> Tournament:
        t = Tournament(tournament_id)
        self._store.save(t)
        return t

    def get(self, tournament_id: str) -> Tournament:
        t = self._store.get(tournament_id)
        if t is None:
            raise NotFound(tournament_id)
        return t

    def registration_open(self, t: Tournament) -> bool:
        if t.status == REGISTERING:
            return True
        return t.status == RUNNING and t.level < LATE_REG_LAST_LEVEL

    def enter(self, tournament_id: str, player: str) -> Entry:
        t = self.get(tournament_id)
        player = player.strip().lower()
        if not self.registration_open(t):
            raise Rejected("registration is closed")
        previous = t.entries_for(player)
        if any(e.live for e in previous):
            raise Rejected(f"{player} already has a live entry")
        if len(previous) > MAX_REENTRIES + 1:
            raise Rejected(f"{player} has used all re-entries")
        entry = Entry(len(t.entries) + 1, player)
        t.entries.append(entry)
        return entry

    def start(self, tournament_id: str) -> Tournament:
        t = self.get(tournament_id)
        if t.status != REGISTERING or len(t.entries) < 2:
            raise Rejected("need at least two entries to start")
        t.status, t.level = RUNNING, 1
        return t

    def next_level(self, tournament_id: str) -> int:
        t = self.get(tournament_id)
        if t.status != RUNNING:
            raise Rejected("tournament is not running")
        t.level += 1
        return t.level
