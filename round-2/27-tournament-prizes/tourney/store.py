from typing import Dict, Optional

from .models import Tournament


class InMemoryStore:
    def __init__(self):
        self.tournaments: Dict[str, Tournament] = {}

    def save(self, t: Tournament) -> None:
        self.tournaments[t.tournament_id] = t

    def get(self, tournament_id: str) -> Optional[Tournament]:
        return self.tournaments.get(tournament_id)
