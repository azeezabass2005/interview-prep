from dataclasses import dataclass
from datetime import date


class LeagueError(Exception):
    pass


@dataclass(frozen=True)
class Result:
    match_id: str
    played_on: date
    home: str
    away: str
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
    deducted: int = 0

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    @property
    def raw_points(self):
        return 3 * self.won + self.drawn

    @property
    def points(self):
        return self.raw_points - self.deducted


class League:
    def __init__(self, teams):
        self.teams = set(teams)
        self.results = []
        self.deductions = {}

    def record(self, match_id, played_on, home, away, home_goals, away_goals):
        if home not in self.teams or away not in self.teams or home == away:
            raise LeagueError("bad teams")
        if home_goals < 0 or away_goals < 0:
            raise LeagueError("bad score")
        self.results.append(Result(match_id, played_on, home, away, home_goals, away_goals))

    def deduct(self, team, points):
        self.deductions[team] = self.deductions.get(team, 0) + points

    def _rows(self):
        rows = {t: Row(t, deducted=self.deductions.get(t, 0)) for t in self.teams}
        for r in self.results:
            home, away = rows[r.home], rows[r.away]
            home.played += 1
            away.played += 1
            home.goals_for += r.home_goals
            home.goals_against += r.away_goals
            away.goals_for += r.away_goals
            away.goals_against += r.away_goals
            if r.home_goals > r.away_goals:
                home.won += 1
                away.lost += 1
            elif r.home_goals < r.away_goals:
                away.won += 1
                home.lost += 1
            else:
                home.drawn += 1
                away.drawn += 1
        return rows

    def table(self):
        rows = self._rows().values()
        return sorted(rows, key=lambda r: (-r.raw_points, -r.goals_for, -r.goal_difference, r.team))

    def form(self, team):
        letters = []
        for r in sorted(self.results, key=lambda r: r.played_on):
            if team not in (r.home, r.away):
                continue
            mine, theirs = (r.home_goals, r.away_goals) if team == r.home else (r.away_goals, r.home_goals)
            letters.append("W" if mine > theirs else "L" if mine < theirs else "D")
        return "".join(letters[-5:])
