FIXES = [
    ("board/repositories/scores.py",
     "    def set_total(self, participant_id: str, score: int) -> None:",
     "    def increment_total(self, participant_id: str, points: int) -> int:\n"
     "        with self._db.transaction() as conn:\n"
     "            return conn.execute(\"UPDATE totals SET score = score + ? WHERE participant_id = ? RETURNING score\",\n"
     "                                (points, participant_id)).fetchone()[0]\n\n"
     "    def set_total(self, participant_id: str, score: int) -> None:"),
    ("board/services/scoring.py",
     "        current = self._scores.total(participant_id)\n        self._scores.set_total(participant_id, current + points)\n"
     "        self._scores.add_weekly(participant_id, week_start(now), points)\n        return current + points",
     "        self._scores.total(participant_id)  # existence check\n"
     "        new_total = self._scores.increment_total(participant_id, points)\n"
     "        self._scores.add_weekly(participant_id, week_start(now), points)\n        return new_total"),
    ("board/services/ranking.py",
     """    standings, rank_no, previous = [], 0, None
    for pid, name, score in rows:
        if score != previous:
            rank_no += 1
            previous = score""",
     """    standings, rank_no, previous = [], 0, None
    for position, (pid, name, score) in enumerate(rows, start=1):
        if score != previous:
            rank_no = position
            previous = score"""),
    ("board/repositories/scores.py", "\"ORDER BY t.score DESC LIMIT ? OFFSET ?\"",
     "\"ORDER BY t.score DESC, p.name, p.participant_id LIMIT ? OFFSET ?\""),
    ("board/services/weeks.py", "    return d - timedelta(days=(d.weekday() + 1) % 7)", "    return d - timedelta(days=d.weekday())"),
]
