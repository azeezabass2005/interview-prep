FIXES = [
    ("league/table.py", "        away.goals_against += r.away_goals\n", "        away.goals_against += r.home_goals\n"),
    ("league/table.py", "            away.points += DRAW\n    return rows",
     "            away.points += DRAW\n    for team, penalty in (deductions or {}).items():\n"
     "        rows.setdefault(team, Row(team)).points -= penalty\n    return rows"),
    ("league/table.py", "    return rows[team].points\n",
     "    points = 0\n"
     "    for r in results:\n"
     "        if not r.played or r.home not in group or r.away not in group or team not in (r.home, r.away):\n"
     "            continue\n"
     "        mine, theirs = (r.home_goals, r.away_goals) if r.home == team else (r.away_goals, r.home_goals)\n"
     "        points += WIN if mine > theirs else DRAW if mine == theirs else 0\n"
     "    return points\n"),
    ("league/table.py", "        return (-row.points, -row.goals_for, -row.goal_difference)",
     "        return (-row.points, -row.goal_difference, -row.goals_for)"),
    ("league/table.py",
     "    table: List[Row] = []\n    for _, group in groupby(ordered, key=level_key):\n        group = list(group)\n"
     "        names = [row.team for row in group]\n"
     "        group.sort(key=lambda row: (-_head_to_head_points(row.team, names, rows, results), row.team))\n"
     "        table.extend(group)\n\n    return [(i + 1, row) for i, row in enumerate(table)]",
     "    table: List[Tuple[int, Row]] = []\n    for _, group in groupby(ordered, key=level_key):\n        group = list(group)\n"
     "        names = [row.team for row in group]\n"
     "        h2h = {row.team: _head_to_head_points(row.team, names, rows, results) for row in group}\n"
     "        group.sort(key=lambda row: (-h2h[row.team], row.team))\n"
     "        start = len(table)\n"
     "        for i, row in enumerate(group):\n"
     "            same_as_prev = i > 0 and h2h[row.team] == h2h[group[i - 1].team]\n"
     "            position = table[-1][0] if same_as_prev else start + i + 1\n"
     "            table.append((position, row))\n\n    return table"),
]
