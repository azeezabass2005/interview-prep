from typing import Dict, List, Optional

from .models import Bowler, MatchResult, Team


class InMemoryStore:
    def __init__(self):
        self.bowlers: Dict[str, Bowler] = {}
        self.teams: Dict[str, Team] = {}
        self.results: List[MatchResult] = []

    def bowler(self, bowler_id: str) -> Optional[Bowler]:
        return self.bowlers.get(bowler_id)

    def team(self, team_id: str) -> Optional[Team]:
        return self.teams.get(team_id)
