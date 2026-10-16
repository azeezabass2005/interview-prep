from datetime import date

from ..errors import LeagueError, NotFound
from ..models import Fixture, Result
from ..store import InMemoryStore


class FixtureService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def add_team(self, name: str) -> None:
        if name in self._store.teams:
            raise LeagueError(f"{name} exists")
        self._store.teams.append(name)

    def schedule(self, fixture_id: str, home: str, away: str, played_on: date) -> Fixture:
        if home == away or home not in self._store.teams or away not in self._store.teams:
            raise LeagueError("fixture needs two different registered teams")
        f = Fixture(fixture_id, home, away, played_on)
        self._store.fixtures[fixture_id] = f
        return f

    def record(self, fixture_id: str, home_goals: int, away_goals: int) -> Result:
        if fixture_id not in self._store.fixtures:
            raise NotFound(fixture_id)
        if home_goals < 0 or away_goals < 0:
            raise LeagueError("goals cannot be negative")
        r = Result(fixture_id, home_goals, away_goals)
        self._store.results.append(r)
        return r

    def deduct(self, team: str, points: int) -> None:
        self._store.deductions[team] = self._store.deductions.get(team, 0) + points
