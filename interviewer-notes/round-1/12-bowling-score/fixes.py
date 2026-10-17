FIXES = [
    ("bowling.py", "            bonus = rolls[i + 2:i + 4]", "            bonus = rolls[i + 2:i + 3]"),
    ("bowling.py", "    while i < len(rolls):\n        frame += 1", "    while i < len(rolls) and frame < FRAMES:\n        frame += 1"),
    ("bowling.py", "            total = _add(total, PINS + sum(bonus), True)", "            total = _add(total, PINS + sum(bonus), len(bonus) == 2)"),
    ("bowling.py", "        return int((HANDICAP_BASIS - average) * HANDICAP_PCT)", "        return max(0, int((HANDICAP_BASIS - average) * HANDICAP_PCT))"),
    ("bowling.py", "        for bowler, score in scratch.items():\n            self.games.setdefault(bowler, []).append(score)\n        result = {}\n        for bowler in (a, b):\n            hcp = self.handicap(bowler)\n",
     "        handicaps = {bowler: self.handicap(bowler) for bowler in (a, b)}\n        for bowler, score in scratch.items():\n            self.games.setdefault(bowler, []).append(score)\n        result = {}\n        for bowler in (a, b):\n            hcp = handicaps[bowler]\n"),
]
