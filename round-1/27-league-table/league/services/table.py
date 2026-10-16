from itertools import groupby
from typing import Dict, List, Tuple

from ..models import Row
from ..store import InMemoryStore

WIN, DRAW = 3, 1


def played_results(store: InMemoryStore):
    for r in store.results:
        yield store.fixtures[r.fixture_id], r


def build_rows(store: InMemoryStore) -> Dict[str, Row]:
    rows = {team: Row(team) for team in store.teams}
    for f, r in played_results(store):
        home, away = rows[f.home], rows[f.away]
        home.played += 1
        away.played += 1
        home.goals_for += r.home_goals
        home.goals_against += r.away_goals
        away.goals_for += r.away_goals
        away.goals_against += r.away_goals
        if r.home_goals > r.away_goals:
            home.won, away.lost, home.points = home.won + 1, away.lost + 1, home.points + WIN
        elif r.home_goals < r.away_goals:
            away.won, home.lost, away.points = away.won + 1, home.lost + 1, away.points + WIN
        else:
            home.drawn, away.drawn = home.drawn + 1, away.drawn + 1
            home.points += DRAW
            away.points += DRAW
    for team, penalty in store.deductions.items():
        rows[team].points -= penalty
    return rows


def head_to_head(store: InMemoryStore, team: str, group: List[str], rows: Dict[str, Row]) -> int:
    return rows[team].points


def standings(store: InMemoryStore) -> List[Tuple[int, Row]]:
    rows = build_rows(store)

    def level(row: Row):
        return (-row.points, -row.goals_for, -row.goal_difference)

    ordered = sorted(rows.values(), key=lambda r: (level(r), r.team))
    table: List[Row] = []
    for _, group in groupby(ordered, key=level):
        group = list(group)
        names = [r.team for r in group]
        group.sort(key=lambda r: (-head_to_head(store, r.team, names, rows), r.team))
        table.extend(group)
    return [(i + 1, row) for i, row in enumerate(table)]


def form(store: InMemoryStore, team: str, last: int = 5) -> str:
    marks = []
    for f, r in sorted(played_results(store), key=lambda fr: fr[0].played_on):
        if team not in (f.home, f.away):
            continue
        mine, theirs = (r.home_goals, r.away_goals) if team == f.home else (r.away_goals, r.home_goals)
        marks.append("W" if mine > theirs else "D" if mine == theirs else "L")
    return "".join(marks[-last:])
