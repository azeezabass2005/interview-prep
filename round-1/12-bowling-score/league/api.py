from .errors import LeagueError
from .game import Game
from .render import symbols
from .services.handicap import average, handicap
from .services.matches import MatchService
from .store import InMemoryStore


class LeagueApi:
    def __init__(self, store: InMemoryStore, matches: MatchService):
        self._store = store
        self._matches = matches

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except LeagueError as exc:
            return exc.status, {"error": str(exc)}

    def score_game(self, rolls):
        def go():
            game = Game(rolls)
            return {"score": game.score(), "frames": game.frame_totals(), "card": symbols(game),
                    "complete": game.is_complete()}
        return self._call(go)

    def add_bowler(self, body: dict):
        return self._call(lambda: {"bowler_id": self._matches.add_bowler(body["bowler_id"], body.get("name", ""),
                                                                          body.get("history", [])).bowler_id}, 201)

    def add_team(self, team_id: str, bowlers):
        return self._call(lambda: {"team_id": self._matches.add_team(team_id, bowlers).team_id}, 201)

    def bowler(self, bowler_id: str):
        def go():
            b = self._store.bowler(bowler_id)
            return {"average": average(b.history), "handicap": handicap(b.history), "games": len(b.history)}
        return self._call(go)

    def record_match(self, body: dict):
        def go():
            r = self._matches.record_match(body["week"], body["home"], body["away"], body["rolls"])
            return {"totals": r.game_totals, "points": r.points}
        return self._call(go, 201)

    def standings(self):
        return self._call(self._matches.standings)
