from itertools import groupby
from typing import Dict, Iterable, List, Optional, Tuple

from .models import Result, Row

WIN, DRAW = 3, 1


def build_rows(results: Iterable[Result], deductions: Optional[Dict[str, int]] = None) -> Dict[str, Row]:
    rows: Dict[str, Row] = {}
    for r in results:
        home = rows.setdefault(r.home, Row(r.home))
        away = rows.setdefault(r.away, Row(r.away))
        if not r.played:
            continue
        home.played += 1
        away.played += 1
        home.goals_for += r.home_goals
        home.goals_against += r.away_goals
        away.goals_for += r.away_goals
        away.goals_against += r.away_goals
        if r.home_goals > r.away_goals:
            home.won += 1
            away.lost += 1
            home.points += WIN
        elif r.home_goals < r.away_goals:
            away.won += 1
            home.lost += 1
            away.points += WIN
        else:
            home.drawn += 1
            away.drawn += 1
            home.points += DRAW
            away.points += DRAW
    return rows


def _head_to_head_points(team: str, group: List[str], rows: Dict[str, Row], results: List[Result]) -> int:
    return rows[team].points


def standings(results: Iterable[Result], deductions: Optional[Dict[str, int]] = None) -> List[Tuple[int, Row]]:
    results = list(results)
    rows = build_rows(results, deductions)

    def level_key(row: Row):
        return (-row.points, -row.goals_for, -row.goal_difference)

    ordered = sorted(rows.values(), key=lambda row: (level_key(row), row.team))
    table: List[Row] = []
    for _, group in groupby(ordered, key=level_key):
        group = list(group)
        names = [row.team for row in group]
        group.sort(key=lambda row: (-_head_to_head_points(row.team, names, rows, results), row.team))
        table.extend(group)

    return [(i + 1, row) for i, row in enumerate(table)]
