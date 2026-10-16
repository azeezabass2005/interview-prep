FIXES = [
    ("league/services/table.py", "        away.goals_against += r.away_goals\n", "        away.goals_against += r.home_goals\n"),
    ("league/services/table.py", "        return (-row.points, -row.goals_for, -row.goal_difference)",
     "        return (-row.points, -row.goal_difference, -row.goals_for)"),
    ("league/services/table.py", "    return rows[team].points\n",
     "    points = 0\n"
     "    for f, r in played_results(store):\n"
     "        if f.home in group and f.away in group and team in (f.home, f.away):\n"
     "            mine, theirs = (r.home_goals, r.away_goals) if team == f.home else (r.away_goals, r.home_goals)\n"
     "            points += WIN if mine > theirs else DRAW if mine == theirs else 0\n"
     "    return points\n"),
    ("league/services/table.py",
     "    table: List[Row] = []\n    for _, group in groupby(ordered, key=level):\n        group = list(group)\n        names = [r.team for r in group]\n"
     "        group.sort(key=lambda r: (-head_to_head(store, r.team, names, rows), r.team))\n        table.extend(group)\n"
     "    return [(i + 1, row) for i, row in enumerate(table)]",
     "    table: List[Tuple[int, Row]] = []\n    for _, group in groupby(ordered, key=level):\n        group = list(group)\n        names = [r.team for r in group]\n"
     "        h2h = {r.team: head_to_head(store, r.team, names, rows) for r in group}\n"
     "        group.sort(key=lambda r: (-h2h[r.team], r.team))\n"
     "        start = len(table)\n"
     "        for i, row in enumerate(group):\n"
     "            same = i > 0 and h2h[row.team] == h2h[group[i - 1].team]\n"
     "            table.append((table[-1][0] if same else start + i + 1, row))\n"
     "    return table"),
    ("league/services/fixtures.py", "        r = Result(fixture_id, home_goals, away_goals)\n        self._store.results.append(r)",
     "        r = Result(fixture_id, home_goals, away_goals)\n"
     "        self._store.results = [x for x in self._store.results if x.fixture_id != fixture_id] + [r]"),
]
