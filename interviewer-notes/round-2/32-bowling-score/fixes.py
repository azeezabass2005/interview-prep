FIXES = [
    ("league/game.py", "        if self.is_complete():\n            raise InvalidRoll(\"game is complete\")\n",
     "        if self.is_complete():\n            raise InvalidRoll(\"game is complete\")\n"
     "        frames = self.frames()\n"
     "        if frames and len(frames) < FRAMES:\n"
     "            _, last = frames[-1]\n"
     "            if len(last) == 1 and last[0] != PINS and last[0] + pins > PINS:\n"
     "                raise InvalidRoll(\"a frame cannot exceed 10 pins\")\n"),
    ("league/game.py", "        frames = self.frames()\n        totals, running = [], 0\n        for idx, (start, rolls) in enumerate(frames):",
     "        frames = self.frames()[:FRAMES]\n        totals, running = [], 0\n        for idx, (start, rolls) in enumerate(frames):"),
    ("league/game.py", "                bonus_rolls = nxt[:2]", "                bonus_rolls = self.rolls[start + 1:start + 3]"),
    ("league/services/matches.py",
     """        for bowler_id, games in scores.items():
            self._store.bowler(bowler_id).history.extend(games)
        totals = [0] * GAMES_PER_SERIES
        for bowler_id, games in scores.items():
            hcp = handicap(self._store.bowler(bowler_id).history)
            for i, score in enumerate(games):
                totals[i] += score + hcp""",
     """        totals = [0] * GAMES_PER_SERIES
        for bowler_id, games in scores.items():
            hcp = handicap(self._store.bowler(bowler_id).history)
            for i, score in enumerate(games):
                totals[i] += score + hcp
        for bowler_id, games in scores.items():
            self._store.bowler(bowler_id).history.extend(games)"""),
    ("league/services/matches.py",
     "            if h >= a:\n                points[home_id] += 1\n            else:\n                points[away_id] += 1",
     "            if h > a:\n                points[home_id] += 1\n            elif a > h:\n                points[away_id] += 1\n"
     "            else:\n                points[home_id] += 0.5\n                points[away_id] += 0.5"),
]
