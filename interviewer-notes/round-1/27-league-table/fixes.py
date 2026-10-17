FIXES = [
    ("standings.py", "            away.goals_against += r.away_goals", "            away.goals_against += r.home_goals"),
    ("standings.py", "(-r.raw_points, -r.goals_for, -r.goal_difference, r.team)", "(-r.points, -r.goal_difference, -r.goals_for, r.team)"),
    ("standings.py", "        self.results.append(Result(", "        self.results = [r for r in self.results if r.match_id != match_id]\n        self.results.append(Result("),
    ("standings.py", "        return \"\".join(letters[-5:])", "        return \"\".join(reversed(letters[-5:]))"),
]
