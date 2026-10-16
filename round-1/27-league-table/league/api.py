from datetime import date

from .errors import LeagueError
from .services.fixtures import FixtureService
from .services.table import form, standings
from .store import InMemoryStore


class LeagueApi:
    def __init__(self, store: InMemoryStore, fixtures: FixtureService):
        self._store = store
        self._fixtures = fixtures

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except LeagueError as exc:
            return exc.status, {"error": str(exc)}

    def teams(self, *names):
        for n in names:
            self._fixtures.add_team(n)
        return 201, {"teams": list(names)}

    def schedule(self, fixture_id, home, away, on):
        return self._call(lambda: {"fixture": self._fixtures.schedule(fixture_id, home, away, date.fromisoformat(on)).fixture_id}, 201)

    def result(self, fixture_id, home_goals, away_goals):
        return self._call(lambda: {"fixture": self._fixtures.record(fixture_id, home_goals, away_goals).fixture_id}, 201)

    def deduct(self, team, points):
        self._fixtures.deduct(team, points)
        return 200, {"team": team}

    def table(self):
        return 200, {"table": [{"pos": pos, "team": r.team, "pts": r.points, "gd": r.goal_difference, "gf": r.goals_for,
                                "played": r.played} for pos, r in standings(self._store)]}

    def form(self, team):
        return 200, {"team": team, "form": form(self._store, team)}
