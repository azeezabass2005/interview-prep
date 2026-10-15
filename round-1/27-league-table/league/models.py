from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Result:
    home: str
    away: str
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None

    @property
    def played(self) -> bool:
        return self.home_goals is not None and self.away_goals is not None


@dataclass
class Row:
    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against
