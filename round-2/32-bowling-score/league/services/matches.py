from typing import Dict, List

from ..errors import LeagueError, NotFound
from ..game import Game
from ..models import Bowler, MatchResult, Team
from ..store import InMemoryStore
from .handicap import handicap

GAMES_PER_SERIES = 3


class MatchService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def add_bowler(self, bowler_id: str, name: str, history=()) -> Bowler:
        bowler = Bowler(bowler_id, name, list(history))
        self._store.bowlers[bowler_id] = bowler
        return bowler

    def add_team(self, team_id: str, bowler_ids) -> Team:
        for bowler_id in bowler_ids:
            if self._store.bowler(bowler_id) is None:
                raise NotFound(f"bowler {bowler_id}")
        team = Team(team_id, list(bowler_ids))
        self._store.teams[team_id] = team
        return team

    def _team_games(self, team: Team, rolls: Dict[str, List[List[int]]]) -> List[int]:
        scores = {}
        for bowler_id in team.bowlers:
            series = rolls.get(bowler_id)
            if series is None or len(series) != GAMES_PER_SERIES:
                raise LeagueError(f"{bowler_id} must bowl {GAMES_PER_SERIES} games")
            games = [Game(r) for r in series]
            if not all(g.is_complete() for g in games):
                raise LeagueError(f"{bowler_id} has an incomplete game")
            scores[bowler_id] = [g.score() for g in games]
        for bowler_id, games in scores.items():
            self._store.bowler(bowler_id).history.extend(games)
        totals = [0] * GAMES_PER_SERIES
        for bowler_id, games in scores.items():
            hcp = handicap(self._store.bowler(bowler_id).history)
            for i, score in enumerate(games):
                totals[i] += score + hcp
        return totals

    def record_match(self, week: int, home_id: str, away_id: str, rolls: Dict[str, List[List[int]]]) -> MatchResult:
        home, away = self._store.team(home_id), self._store.team(away_id)
        if home is None or away is None:
            raise NotFound("unknown team")
        home_totals = self._team_games(home, rolls)
        away_totals = self._team_games(away, rolls)
        points = {home_id: 0.0, away_id: 0.0}
        for h, a in list(zip(home_totals, away_totals)) + [(sum(home_totals), sum(away_totals))]:
            if h >= a:
                points[home_id] += 1
            else:
                points[away_id] += 1
        result = MatchResult(week, home_id, away_id, {home_id: home_totals, away_id: away_totals}, points)
        self._store.results.append(result)
        return result

    def standings(self) -> Dict[str, float]:
        table: Dict[str, float] = {}
        for result in self._store.results:
            for team, pts in result.points.items():
                table[team] = table.get(team, 0) + pts
        return dict(sorted(table.items(), key=lambda kv: (-kv[1], kv[0])))
