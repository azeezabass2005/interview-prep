FIXES = [
    ("tourney/services/pool.py", "    return max(prize_side(entry_count), GUARANTEE_CENTS) - rake(entry_count)",
     "    return max(prize_side(entry_count) - rake(entry_count), GUARANTEE_CENTS)"),
    ("tourney/services/pool.py", "entry_count < max_entries:", "entry_count <= max_entries:"),
    ("tourney/services/results.py", "        for player in players:\n            prizes[player] = covered[0]",
     "        prizes.update(split_evenly(sum(covered), players))"),
    ("tourney/services/registration.py", "if len(previous) > MAX_REENTRIES + 1:", "if len(previous) > MAX_REENTRIES:"),
    ("tourney/services/registration.py", "t.level < LATE_REG_LAST_LEVEL", "t.level <= LATE_REG_LAST_LEVEL"),
]
