from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Bowler:
    bowler_id: str
    name: str
    history: List[int] = field(default_factory=list)


@dataclass
class Team:
    team_id: str
    bowlers: List[str]


@dataclass
class MatchResult:
    week: int
    home: str
    away: str
    game_totals: Dict[str, List[int]]
    points: Dict[str, float]
