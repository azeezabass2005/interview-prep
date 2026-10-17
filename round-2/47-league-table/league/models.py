from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Fixture:
    fixture_id: str
    home: str
    away: str
    played_on: date


@dataclass(frozen=True)
class Result:
    fixture_id: str
    home_goals: int
    away_goals: int


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
